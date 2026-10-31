import hashlib
import json
import os
from pathlib import Path
from typing import Protocol

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


class ChatClient(Protocol):
    def complete(
        self, messages: list[dict[str, str]], *, temperature: float = 0.0, max_tokens: int = 512
    ) -> str: ...


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        return code == 429 or code >= 500
    return False


class OpenAICompatClient:
    """Chat Completions client. Meta Model API, Modal Endpoints and vLLM all speak this."""

    def __init__(
        self,
        model_id: str,
        base_url: str,
        api_key: str,
        cache_dir: Path | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.model_id = model_id
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.cache_dir = cache_dir
        self._http = httpx.Client(timeout=timeout)

    def complete(
        self, messages: list[dict[str, str]], *, temperature: float = 0.0, max_tokens: int = 512
    ) -> str:
        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        cache_file = self._cache_path(payload)
        if cache_file and cache_file.exists():
            return json.loads(cache_file.read_text(encoding="utf-8"))["output"]
        output = self._post(payload)
        if cache_file:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps({"output": output}, ensure_ascii=False), "utf-8")
        return output

    def _cache_path(self, payload: dict) -> Path | None:
        if not self.cache_dir or payload["temperature"] > 0:
            return None
        blob = json.dumps([self.base_url, payload], sort_keys=True, ensure_ascii=False)
        return self.cache_dir / f"{hashlib.sha256(blob.encode()).hexdigest()}.json"

    @retry(
        retry=retry_if_exception(_retryable),
        stop=stop_after_attempt(4),
        wait=wait_exponential(min=2, max=30),
        reraise=True,
    )
    def _post(self, payload: dict) -> str:
        resp = self._http.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"] or ""


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set; copy .env.example to .env and export it")
    return value

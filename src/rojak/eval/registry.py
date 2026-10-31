import os
from pathlib import Path

import yaml

from ..llm import ChatClient, OpenAICompatClient, require_env


def load_config(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_client(spec: dict, cache_dir: Path | None) -> ChatClient:
    base_url = spec.get("base_url") or require_env(spec["base_url_env"])
    return OpenAICompatClient(
        model_id=spec["model_id"],
        base_url=base_url,
        api_key=require_env(spec["api_key_env"]),
        cache_dir=cache_dir,
    )


def available_models(config: dict) -> list[str]:
    """Models whose endpoint and key env vars are actually set, so 'all' skips unconfigured ones."""
    names = []
    for name, spec in config["models"].items():
        needs = [spec["api_key_env"]] + ([spec["base_url_env"]] if "base_url_env" in spec else [])
        if all(os.environ.get(var) for var in needs):
            names.append(name)
    return names

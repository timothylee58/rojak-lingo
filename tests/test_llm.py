from rojak.llm import OpenAICompatClient


def test_complete_default_budget_fits_reasoning_models(monkeypatch):
    """Eval calls complete() with defaults; 512 tokens leaves reasoning models
    no room for content (finish_reason=length, content=null)."""
    client = OpenAICompatClient(model_id="m", base_url="http://x", api_key="k")
    seen: dict = {}
    monkeypatch.setattr(client, "_post", lambda payload: seen.update(payload) or "ok")
    assert client.complete([{"role": "user", "content": "hi"}]) == "ok"
    assert seen["max_tokens"] == 4096

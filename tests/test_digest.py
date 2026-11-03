import json

from rojak.report.examples import build_digest


def test_digest_covers_all_gold_ids_with_per_model_outputs(tmp_path):
    gold = tmp_path / "gold"
    gold.mkdir()
    (gold / "intent.jsonl").write_text(
        json.dumps({"id": "a", "task": "intent", "prompt": "hi?", "reference": "other"})
        + "\n",
        encoding="utf-8",
    )
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "m.jsonl").write_text(
        json.dumps({"id": "a", "task": "intent", "model": "m", "output": "other", "score": 1.0})
        + "\n",
        encoding="utf-8",
    )
    d = build_digest(gold, runs)
    assert d["models"] == ["m"]
    assert len(d["items"]) == 1
    item = d["items"][0]
    assert (item["prompt"], item["reference"]) == ("hi?", "other")
    assert item["outputs"]["m"] == {"output": "other", "score": 1.0}

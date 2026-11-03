"""Build web/public/examples.json: every gold item with each model's output.

Published alongside leaderboard.json so the Examples page can show side-by-side
outputs. Reads results/runs/*.jsonl (per-item outputs) and data/gold/*.jsonl
(prompts and references).
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import typer

app = typer.Typer(add_completion=False)


def build_digest(gold_dir: Path, runs_dir: Path) -> dict:
    items: dict[str, dict] = {}
    for path in sorted(gold_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            items[r["id"]] = {
                "id": r["id"],
                "task": r["task"],
                "prompt": r["prompt"],
                "reference": r["reference"],
                "outputs": {},
            }
    models: list[str] = []
    for path in sorted(runs_dir.glob("*.jsonl")):
        models.append(path.stem)
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r["id"] in items:
                items[r["id"]]["outputs"][path.stem] = {
                    "output": r["output"],
                    "score": r["score"],
                }
    return {
        "generated": datetime.now(UTC).isoformat(),
        "models": models,
        "items": [items[k] for k in sorted(items)],
    }


@app.command()
def main(
    gold_dir: Path = Path("data/gold"),
    runs_dir: Path = Path("results/runs"),
    out: Path = Path("web/public/examples.json"),
) -> None:
    digest = build_digest(gold_dir, runs_dir)
    out.write_text(json.dumps(digest, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out} with {len(digest['items'])} items x {len(digest['models'])} models")


if __name__ == "__main__":
    app()

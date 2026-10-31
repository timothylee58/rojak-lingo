import json
from datetime import UTC, datetime
from pathlib import Path


def main(results_dir: Path = Path("results")) -> None:
    summaries = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted((results_dir / "summary").glob("*.json"))
    ]
    board = {
        "generated": datetime.now(UTC).isoformat(),
        "models": {s["model"]: s for s in summaries},
    }
    out = results_dir / "leaderboard.json"
    out.write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out} with {len(summaries)} models")


if __name__ == "__main__":
    main()

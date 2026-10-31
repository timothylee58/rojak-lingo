import json
from collections.abc import Iterable
from pathlib import Path

from .schema import Item


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def load_gold(gold_dir: Path = Path("data/gold")) -> list[Item]:
    items: list[Item] = []
    for path in sorted(gold_dir.glob("*.jsonl")):
        items.extend(Item(**row) for row in read_jsonl(path))
    return items

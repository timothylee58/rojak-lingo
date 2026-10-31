import json
import sys
from pathlib import Path

import typer

from ..io import load_gold, read_jsonl, write_jsonl
from ..schema import Item, TaskType
from ..text import ngrams, tokens

app = typer.Typer(add_completion=False)
N = 5
TEXT_TASKS = (TaskType.normalize, TaskType.translate)


def gold_texts(item: Item) -> list[str]:
    # Intent references are bare labels and instruct references are JSON checks;
    # only normalize/translate targets are natural text that can leak.
    return [item.prompt] + ([item.reference] if item.task in TEXT_TASKS else [])


def train_texts(row: dict) -> list[str]:
    task = TaskType(row["task"])
    return [row["prompt"]] + ([row["response"]] if task in TEXT_TASKS else [])


def build_index(items: list[Item]) -> tuple[list[set], dict[tuple, list[int]]]:
    grams: list[set] = []
    index: dict[tuple, list[int]] = {}
    for item in items:
        for text in gold_texts(item):
            g = ngrams(tokens(text), N)
            for gram in g:
                index.setdefault(gram, []).append(len(grams))
            grams.append(g)
    return grams, index


def overlap(row: dict, grams: list[set], index: dict, threshold: float) -> float:
    worst = 0.0
    for text in train_texts(row):
        t = ngrams(tokens(text), N)
        hits: dict[int, int] = {}
        for gram in t:
            for gid in index.get(gram, []):
                hits[gid] = hits.get(gid, 0) + 1
        for gid, count in hits.items():
            worst = max(worst, count / min(len(t), len(grams[gid])))
    return worst


@app.command()
def main(
    train_file: Path = Path("data/synthetic/train.jsonl"),
    gold_dir: Path = Path("data/gold"),
    threshold: float = typer.Option(0.5, help="max allowed n-gram overlap with any gold text"),
    drop: bool = typer.Option(False, help="write a cleaned file and exit 0"),
    allow_missing_train: bool = typer.Option(False, help="exit 0 if there is no train file yet"),
    report: Path = Path("results/contamination.json"),
) -> None:
    if not train_file.exists():
        typer.echo(f"{train_file} not found")
        sys.exit(0 if allow_missing_train else 1)

    grams, index = build_index(load_gold(gold_dir))
    rows = read_jsonl(train_file)
    scored = [(row, overlap(row, grams, index, threshold)) for row in rows]
    flagged = [(row, s) for row, s in scored if s >= threshold]

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps(
            {
                "train_rows": len(rows),
                "flagged": len(flagged),
                "threshold": threshold,
                "examples": [{"prompt": r["prompt"], "overlap": round(s, 3)} for r, s in flagged[:20]],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    typer.echo(f"{len(rows)} train rows, {len(flagged)} flagged (overlap >= {threshold})")

    if drop:
        clean = [row for row, s in scored if s < threshold]
        write_jsonl(train_file.with_name("train.clean.jsonl"), clean)
        typer.echo(f"wrote {len(clean)} rows to train.clean.jsonl")
        return
    if flagged:
        sys.exit(1)


if __name__ == "__main__":
    app()

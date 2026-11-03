import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import typer

from ..io import load_gold, write_jsonl
from ..schema import Item, Status, TaskType
from ..tasks.prompts import build_messages
from .metrics import aggregate, score_item
from .registry import available_models, build_client, load_config

app = typer.Typer(add_completion=False)


def oracle_output(item: Item) -> str:
    """Perfect answer per task, used with --mock to prove the pipeline end to end offline."""
    if item.task != TaskType.instruct:
        return item.reference
    checks = json.loads(item.reference)
    return " ".join([checks.get("starts_with", ""), *checks.get("must_include", [])]).strip()


def run_model(
    name: str, complete, items: list[Item], workers: int = 8, style: str = "zero"
) -> dict[str, str]:
    def one(item: Item) -> tuple[str, str]:
        return item.id, complete(build_messages(item.task, item.prompt, style))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(pool.map(one, items))


@app.command()
def main(
    models: str = typer.Option("all", help="comma-separated names from the config, or 'all'"),
    limit: int = typer.Option(0, help="evaluate only the first N items (cheap smoke test)"),
    gold_dir: Path = Path("data/gold"),
    config: Path = Path("configs/models.yaml"),
    out_dir: Path = Path("results"),
    mock: bool = typer.Option(False, help="offline oracle model, no API calls"),
    only_verified: bool = typer.Option(False, help="skip gold items not yet hand-verified"),
) -> None:
    items = load_gold(gold_dir)
    if only_verified:
        items = [i for i in items if i.status == Status.verified]
    if limit:
        items = items[:limit]
    drafts = sum(i.status == Status.draft for i in items)

    cfg = load_config(config)
    if mock:
        names = ["oracle"]
    elif models == "all":
        names = available_models(cfg)
    else:
        names = [m.strip() for m in models.split(",")]
    if not names:
        raise typer.BadParameter("no models configured; set the env vars in .env.example")

    for name in names:
        if mock:
            by_id = {i.id: oracle_output(i) for i in items}
            outputs = by_id
        else:
            client = build_client(cfg["models"][name], out_dir / "cache")
            style = cfg["models"][name].get("prompt_style", "zero")
            outputs = run_model(name, lambda m, c=client: c.complete(m), items, style=style)

        write_jsonl(
            out_dir / "runs" / f"{name}.jsonl",
            ({"id": i.id, "task": i.task.value, "output": outputs[i.id],
              "score": score_item(i, outputs[i.id])} for i in items),
        )
        summary = {
            "model": name,
            "created": datetime.now(UTC).isoformat(),
            "n_items": len(items),
            "n_draft_items": drafts,
            "metrics": aggregate(items, outputs),
        }
        path = out_dir / "summary" / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        typer.echo(f"{name}: {json.dumps(summary['metrics'], ensure_ascii=False)}")


if __name__ == "__main__":
    app()

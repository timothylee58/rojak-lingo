"""Paired significance tests for model comparisons.

Reads results/runs/*.jsonl and, per task, compares every pair of models on the
items they share. Binary per-item scores (intent accuracy, instruct pass/fail)
use McNemar's exact test; continuous scores (chrF) use a paired bootstrap CI
on the mean difference.
"""

import json
import math
import random
from itertools import combinations
from pathlib import Path

import typer

app = typer.Typer(add_completion=False)

BINARY_TASKS = ("intent", "instruct")
N_BOOT = 10_000


def mcnemar_p(b: int, c: int) -> float:
    """Two-sided exact p-value. b = A wrong/B right, c = A right/B wrong."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2**n
    return min(1.0, 2 * tail)


def bootstrap_ci(diffs: list[float], n_boot: int = N_BOOT, seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(diffs)
    stats = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    return stats[int(0.025 * n_boot)], stats[int(0.975 * n_boot) - 1]


def compare(task: str, a: dict[str, float], b: dict[str, float]) -> dict:
    ids = sorted(set(a) & set(b))
    da = [a[i] for i in ids]
    db = [b[i] for i in ids]
    out: dict = {
        "n": len(ids),
        "mean_a": sum(da) / len(da),
        "mean_b": sum(db) / len(db),
        "diff": sum(da) / len(da) - sum(db) / len(db),
    }
    if task in BINARY_TASKS:
        wrong_a_right_b = sum(1 for x, y in zip(da, db) if x < y)
        right_a_wrong_b = sum(1 for x, y in zip(da, db) if x > y)
        out["mcnemar_p"] = mcnemar_p(wrong_a_right_b, right_a_wrong_b)
        out["significant"] = out["mcnemar_p"] < 0.05
    else:
        lo, hi = bootstrap_ci([x - y for x, y in zip(da, db)])
        out["ci_lo"], out["ci_hi"] = lo, hi
        out["significant"] = lo > 0 or hi < 0
    return out


def load_runs(runs_dir: Path) -> dict[str, dict[str, dict[str, float]]]:
    models: dict[str, dict[str, dict[str, float]]] = {}
    for path in sorted(runs_dir.glob("*.jsonl")):
        per_task: dict[str, dict[str, float]] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            per_task.setdefault(r["task"], {})[r["id"]] = r["score"]
        models[path.stem] = per_task
    return models


@app.command()
def main(
    runs_dir: Path = Path("results/runs"),
    out: Path = Path("results/significance.json"),
) -> None:
    models = load_runs(runs_dir)
    names = sorted(models)
    report: dict = {"models": names, "tasks": {}}
    for task in ("normalize", "intent", "instruct", "translate"):
        pairs = {}
        for a, b in combinations(names, 2):
            if task in models[a] and task in models[b]:
                pairs[f"{a} vs {b}"] = compare(task, models[a][task], models[b][task])
        report["tasks"][task] = pairs
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    for task, pairs in report["tasks"].items():
        typer.echo(f"== {task} ==")
        for name, r in pairs.items():
            if "mcnemar_p" in r:
                sig = "SIGNIFICANT" if r["significant"] else "ns"
                typer.echo(
                    f"  {name}: diff {r['diff']:+.3f} "
                    f"({r['mean_a']:.3f} vs {r['mean_b']:.3f}, n={r['n']}) "
                    f"McNemar p={r['mcnemar_p']:.4f} [{sig}]"
                )
            else:
                sig = "SIGNIFICANT" if r["significant"] else "ns"
                typer.echo(
                    f"  {name}: diff {r['diff']:+.3f} "
                    f"95% CI [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] [{sig}]"
                )
    typer.echo(f"wrote {out}")


if __name__ == "__main__":
    app()

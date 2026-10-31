import json
import sys
from collections import Counter
from pathlib import Path

from .eval.metrics import ALLOWED_CHECKS
from .io import load_gold
from .schema import Status, TaskType


def main(gold_dir: Path = Path("data/gold")) -> int:
    items = load_gold(gold_dir)
    errors: list[str] = []

    ids = Counter(i.id for i in items)
    errors += [f"duplicate id: {k}" for k, v in ids.items() if v > 1]

    prompts = Counter(i.prompt.strip().lower() for i in items)
    errors += [f"duplicate prompt: {k[:40]}" for k, v in prompts.items() if v > 1]

    for item in items:
        if item.task == TaskType.instruct:
            try:
                checks = json.loads(item.reference)
            except json.JSONDecodeError:
                errors.append(f"{item.id}: reference is not valid JSON")
                continue
            unknown = set(checks) - ALLOWED_CHECKS
            if unknown:
                errors.append(f"{item.id}: unknown checks {sorted(unknown)}")

    by_task = Counter(i.task.value for i in items)
    verified = sum(i.status == Status.verified for i in items)
    print(f"gold items: {len(items)} | verified: {verified} | draft: {len(items) - verified}")
    for task, count in sorted(by_task.items()):
        print(f"  {task}: {count}")
    for err in errors:
        print(f"ERROR {err}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

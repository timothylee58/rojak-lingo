import json
import re
from collections import defaultdict

from sacrebleu.metrics import CHRF
from sklearn.metrics import f1_score

from ..schema import INTENT_LABELS, Item, TaskType

_chrf = CHRF()
_WORD = re.compile(r"[一-鿿]|[^\s一-鿿]+")
_SENTENCE_END = re.compile(r"[.!?。！？]+")

ALLOWED_CHECKS = {
    "must_include",
    "must_not_include",
    "max_words",
    "min_words",
    "max_sentences",
    "starts_with",
}


def chrf(pred: str, ref: str) -> float:
    return _chrf.sentence_score(pred.strip(), [ref]).score / 100


def extract_intent(output: str) -> str:
    low = output.lower()
    best, pos = "invalid", len(low) + 1
    for label in INTENT_LABELS:
        idx = low.find(label)
        if idx != -1 and idx < pos:
            best, pos = label, idx
    return best


def count_words(text: str) -> int:
    return len(_WORD.findall(text))


def count_sentences(text: str) -> int:
    return len([s for s in _SENTENCE_END.split(text) if s.strip()])


def check_constraints(output: str, checks: dict) -> dict[str, bool]:
    low = output.lower().strip()
    results: dict[str, bool] = {}
    for key, value in checks.items():
        if key == "must_include":
            results[key] = all(str(v).lower() in low for v in value)
        elif key == "must_not_include":
            results[key] = all(str(v).lower() not in low for v in value)
        elif key == "max_words":
            results[key] = count_words(output) <= value
        elif key == "min_words":
            results[key] = count_words(output) >= value
        elif key == "max_sentences":
            results[key] = count_sentences(output) <= value
        elif key == "starts_with":
            results[key] = low.startswith(str(value).lower())
        else:
            raise ValueError(f"unknown check: {key}")
    return results


def score_item(item: Item, output: str) -> float:
    if item.task in (TaskType.normalize, TaskType.translate):
        return chrf(output, item.reference)
    if item.task == TaskType.intent:
        return float(extract_intent(output) == item.reference)
    checks = json.loads(item.reference)
    return float(all(check_constraints(output, checks).values()))


def aggregate(items: list[Item], outputs: dict[str, str]) -> dict[str, dict[str, float]]:
    by_task: dict[TaskType, list[Item]] = defaultdict(list)
    for item in items:
        if item.id in outputs:
            by_task[item.task].append(item)

    summary: dict[str, dict[str, float]] = {}
    for task, task_items in by_task.items():
        scores = [score_item(i, outputs[i.id]) for i in task_items]
        entry = {"n": float(len(task_items))}
        if task == TaskType.intent:
            preds = [extract_intent(outputs[i.id]) for i in task_items]
            refs = [i.reference for i in task_items]
            entry["accuracy"] = sum(s for s in scores) / len(scores)
            entry["macro_f1"] = float(
                f1_score(refs, preds, labels=list(INTENT_LABELS), average="macro", zero_division=0)
            )
        elif task == TaskType.instruct:
            entry["pass_rate"] = sum(scores) / len(scores)
        else:
            entry["chrf"] = sum(scores) / len(scores)
        summary[task.value] = entry
    return summary

import json
import random
from pathlib import Path

import typer

from ..eval.metrics import ALLOWED_CHECKS, check_constraints
from ..eval.registry import build_client, load_config
from ..io import write_jsonl
from ..schema import INTENT_LABELS, TaskType
from ..tasks.prompts import build_messages
from .dedupe import dedupe

app = typer.Typer(add_completion=False)

# Reasoning teachers can spend half the budget thinking; 20 instruct items need the headroom.
TEACHER_MAX_TOKENS = 8192
FETCH_ATTEMPTS = 3

SCENARIOS = [
    "ordering food at a mamak or hawker stall", "traffic and commuting in Klang Valley",
    "workplace chat about deadlines", "e-wallet and online banking", "Grab rides and delivery",
    "condo management and neighbours", "school and university life", "renting a room",
    "LRT and MRT", "public holidays and balik kampung", "online shopping and parcels",
    "football and badminton", "WhatsApp family group", "customer support for a telco",
    "cafe and kopitiam", "weather and haze", "gym and health", "weekend trips", "salary and bills",
    "product reviews on social media",
]
MIXES = [
    "English with Bahasa Malaysia words", "English with Mandarin words",
    "Bahasa Malaysia with English words", "English, Bahasa Malaysia and Mandarin together",
    "English with Cantonese words", "mostly English with lah / lor / meh particles",
]
REGISTERS = ["casual WhatsApp chat", "customer service message", "workplace chat", "social media comment"]

# Gold items are never shown to the teacher. Showing them would leak the test set into
# training data and invalidate the benchmark.
INSTRUCTIONS = {
    TaskType.normalize: (
        'Each item: {{"rojak": <code-switched message>, "standard": <same meaning in clear standard English>}}.'
    ),
    TaskType.intent: (
        'Each item: {{"text": <code-switched customer message>, "label": one of '
        + str(list(INTENT_LABELS)) + "}}. Balance the labels."
    ),
    TaskType.translate: (
        'Each item: {{"source": <short sentence in one language, may include slang>, '
        '"target_lang": one of ["English", "Bahasa Malaysia", "Mandarin (Simplified)"], '
        '"translation": <faithful translation into target_lang>}}.'
    ),
    TaskType.instruct: (
        'Each item: {{"instruction": <a short writing request in English, BM or Mandarin>, '
        '"checks": <object using only these keys: ' + str(sorted(ALLOWED_CHECKS)) + ">, "
        '"response": <an answer that satisfies every check>}}.'
    ),
}


def teacher_messages(
    task: TaskType, n: int, rng: random.Random, mixes: list[str] | None = None
) -> list[dict[str, str]]:
    pool = [m for m in MIXES if mixes is None or any(s.lower() in m.lower() for s in mixes)]
    scenario, mix, register = rng.choice(SCENARIOS), rng.choice(pool or MIXES), rng.choice(REGISTERS)
    user = (
        f"Generate {n} diverse items for a Malaysian code-switching dataset.\n"
        f"Topic: {scenario}. Language mix: {mix}. Style: {register}.\n"
        f"{INSTRUCTIONS[task].format()}\n"
        "Return only a JSON array, no prose."
    )
    return [
        {"role": "system", "content": "You write realistic, natural Malaysian text. Output valid JSON only."},
        {"role": "user", "content": user},
    ]


def parse_json_array(text: str) -> list[dict]:
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end <= start:
        return []
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []
    return [d for d in data if isinstance(d, dict)]


def to_row(task: TaskType, d: dict, teacher: str) -> dict | None:
    """Convert a teacher item to a training row, or None if it fails verification."""
    try:
        if task == TaskType.normalize:
            prompt, response = d["rojak"], d["standard"]
        elif task == TaskType.intent:
            prompt, response = d["text"], d["label"]
            if response not in INTENT_LABELS:
                return None
        elif task == TaskType.translate:
            prompt = f"Translate into {d['target_lang']}: {d['source']}"
            response = d["translation"]
        else:
            checks = d["checks"]
            if not isinstance(checks, dict) or not set(checks) <= ALLOWED_CHECKS:
                return None
            prompt, response = d["instruction"], d["response"]
            # Rejection sampling: only keep answers that provably satisfy their own checks.
            if not all(check_constraints(response, checks).values()):
                return None
    except (KeyError, TypeError, ValueError):
        return None
    if not all(isinstance(x, str) and x.strip() for x in (prompt, response)):
        return None
    messages = build_messages(task, prompt) + [{"role": "assistant", "content": response}]
    return {"task": task.value, "prompt": prompt, "response": response, "messages": messages, "teacher": teacher}


def fetch_items(
    client, task: TaskType, n: int, rng: random.Random, mixes: list[str] | None = None
) -> tuple[list[dict], int]:
    """One teacher call with retries: truncated JSON parses to nothing, so retry instead of
    losing the whole call. Returns (items, retries_used)."""
    for attempt in range(FETCH_ATTEMPTS):
        items = parse_json_array(
            client.complete(
                teacher_messages(task, n, rng, mixes),
                temperature=0.9,
                max_tokens=TEACHER_MAX_TOKENS,
            )
        )
        if items:
            return items, attempt
    return [], FETCH_ATTEMPTS - 1


def mock_items(task: TaskType, n: int, rng: random.Random) -> list[dict]:
    """Deterministic fake teacher so the whole pipeline can be tested offline."""
    out = []
    for _ in range(n):
        k = rng.randint(0, 10**6)
        if task == TaskType.normalize:
            out.append({"rojak": f"Eh later we makan at stall {k} lah", "standard": f"Let's eat at stall {k} later."})
        elif task == TaskType.intent:
            out.append({"text": f"Order {k} lambat betul", "label": rng.choice(INTENT_LABELS)})
        elif task == TaskType.translate:
            out.append({"source": f"Terima kasih {k}", "target_lang": "English", "translation": f"Thank you {k}"})
        else:
            out.append({"instruction": f"Say hello {k} and mention kopi.", "checks": {"must_include": ["kopi"]},
                        "response": f"Hello {k}, mari minum kopi."})
    return out


@app.command()
def main(
    tasks: str = "normalize,intent,instruct,translate",
    calls_per_task: int = typer.Option(30, help="teacher calls per task"),
    items_per_call: int = 20,
    mixes: str = typer.Option("", help="comma-separated substrings to restrict language mixes"),
    out: Path = Path("data/synthetic/train.jsonl"),
    config: Path = Path("configs/models.yaml"),
    seed: int = 7,
    mock: bool = False,
) -> None:
    rng = random.Random(seed)
    mix_filter = [s.strip() for s in mixes.split(",") if s.strip()] or None
    cfg = load_config(config)
    teacher = cfg["teacher"]
    client = None if mock else build_client(cfg["models"][teacher], Path("results/cache"))

    rows: list[dict] = []
    for name in tasks.split(","):
        task = TaskType(name.strip())
        generated = rejected = retries = 0
        task_rows: list[dict] = []
        for _ in range(calls_per_task):
            if mock:
                items = mock_items(task, items_per_call, rng)
            else:
                # temperature > 0 for variety; this also bypasses the response cache on purpose
                items, used = fetch_items(client, task, items_per_call, rng, mix_filter)
                retries += used
            for d in items:
                generated += 1
                row = to_row(task, d, "mock" if mock else cfg["models"][teacher]["model_id"])
                if row:
                    task_rows.append(row)
                else:
                    rejected += 1
        kept, dupes = dedupe(task_rows)
        typer.echo(
            f"{task.value}: generated {generated}, rejected {rejected}, "
            f"duplicates {dupes}, retries {retries}, kept {len(kept)}"
        )
        rows += kept

    typer.echo(f"wrote {write_jsonl(out, rows)} rows to {out}")


if __name__ == "__main__":
    app()

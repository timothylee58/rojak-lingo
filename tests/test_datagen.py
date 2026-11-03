import json

from typer.testing import CliRunner

from rojak.datagen.contamination import app as contamination_app
from rojak.datagen.dedupe import dedupe
from rojak.datagen.generate import (
    TEACHER_MAX_TOKENS,
    fetch_items,
    parse_json_array,
    teacher_messages,
    to_row,
)
from rojak.datagen.generate import app as generate_app
from rojak.io import read_jsonl, write_jsonl
from rojak.schema import TaskType

runner = CliRunner()


def test_dedupe_drops_exact_and_near_duplicates():
    rows = [
        {"prompt": "Eh later we go makan lah, I am starving already"},
        {"prompt": "Eh later we go makan lah, I am starving already!"},
        {"prompt": "Eh later we go makan lah I am starving already ok"},
        {"prompt": "Completely different sentence about the LRT being late today"},
    ]
    kept, dropped = dedupe(rows)
    assert dropped == 2
    assert len(kept) == 2


def test_parse_json_array_tolerates_prose():
    text = 'Sure! Here you go:\n[{"a": 1}, {"a": 2}]\nHope that helps'
    assert parse_json_array(text) == [{"a": 1}, {"a": 2}]
    assert parse_json_array("no json here") == []


def test_to_row_rejects_instruct_answers_that_break_their_checks():
    good = {"instruction": "Say hi", "checks": {"must_include": ["kopi"]}, "response": "minum kopi"}
    bad = {"instruction": "Say hi", "checks": {"must_include": ["kopi"]}, "response": "hello"}
    assert to_row(TaskType.instruct, good, "t") is not None
    assert to_row(TaskType.instruct, bad, "t") is None


def test_to_row_rejects_invalid_intent_label():
    assert to_row(TaskType.intent, {"text": "hi", "label": "angry"}, "t") is None


def test_teacher_messages_mix_filter_restricts_mixes():
    import random

    msgs = teacher_messages(TaskType.normalize, 1, random.Random(0), ["cantonese"])
    assert "Cantonese" in msgs[1]["content"]
    msgs = teacher_messages(TaskType.normalize, 1, random.Random(0), ["zzz-no-match"])
    assert isinstance(msgs[1]["content"], str)  # falls back to full pool, never crashes


def test_fetch_items_retries_truncated_json_with_big_budget():
    import random

    seen: list[dict] = []
    answers = iter(['[{"rojak": "truncated'] * 3)  # all 3 attempts unparseable

    class Stub:
        def complete(self, messages, temperature=0.0, max_tokens=4096):
            seen.append({"temperature": temperature, "max_tokens": max_tokens})
            return next(answers)

    items, retries = fetch_items(Stub(), TaskType.normalize, 1, random.Random(0))
    assert items == [] and retries == 2  # 3 attempts, all unparseable
    assert all(s["max_tokens"] == TEACHER_MAX_TOKENS == 8192 for s in seen)

    answers2 = iter(['[{"broken"', '[{"rojak": "a", "standard": "b"}]'])

    class Stub2(Stub):
        def complete(self, messages, temperature=0.0, max_tokens=4096):
            return next(answers2)

    items, retries = fetch_items(Stub2(), TaskType.normalize, 1, random.Random(0))
    assert len(items) == 1 and retries == 1


def test_contamination_flags_leaked_gold_and_drop_cleans(tmp_path):
    gold = tmp_path / "gold"
    gold.mkdir()
    write_jsonl(
        gold / "g.jsonl",
        [{
            "id": "n-1", "task": "normalize",
            "prompt": "Eh bro later we go makan lah I am starving already",
            "reference": "Hey let us go eat later I am already starving",
            "languages": ["en"],
        }],
    )
    train = tmp_path / "train.jsonl"
    write_jsonl(
        train,
        [
            {"task": "normalize", "prompt": "Eh bro later we go makan lah I am starving already",
             "response": "x y z"},
            {"task": "normalize", "prompt": "Aiya the LRT delay again so annoying today", "response": "a b c"},
        ],
    )
    args = ["--train-file", str(train), "--gold-dir", str(gold), "--report", str(tmp_path / "r.json")]
    assert runner.invoke(contamination_app, args).exit_code == 1
    assert runner.invoke(contamination_app, [*args, "--drop"]).exit_code == 0
    assert len(read_jsonl(tmp_path / "train.clean.jsonl")) == 1


def test_missing_train_file_allowed_flag(tmp_path):
    args = ["--train-file", str(tmp_path / "nope.jsonl"), "--allow-missing-train"]
    assert runner.invoke(contamination_app, args).exit_code == 0


def test_generate_mock_end_to_end(tmp_path):
    out = tmp_path / "train.jsonl"
    result = runner.invoke(
        generate_app,
        ["--mock", "--calls-per-task", "2", "--items-per-call", "5", "--out", str(out)],
    )
    assert result.exit_code == 0, result.output
    rows = read_jsonl(out)
    assert rows and {"task", "prompt", "response", "messages"} <= set(rows[0])
    assert json.dumps(rows[0]["messages"][-1]["role"]) == '"assistant"'

import json

import pytest

from rojak.eval.metrics import (
    aggregate,
    check_constraints,
    chrf,
    count_sentences,
    count_words,
    extract_intent,
)
from rojak.schema import Item


def make(task, prompt, reference, id_="x"):
    return Item(id=id_, task=task, prompt=prompt, reference=reference, languages=["en"])


def test_extract_intent_picks_earliest_label():
    assert extract_intent("Complaint, not a request") == "complaint"
    assert extract_intent("I think this is praise.") == "praise"
    assert extract_intent("no idea") == "invalid"


def test_count_words_handles_cjk_and_latin():
    assert count_words("Selamat pagi boss") == 3
    assert count_words("椰浆饭很好吃") == 6
    assert count_words("mix 椰浆饭 ok") == 5


def test_count_sentences_handles_chinese_punctuation():
    assert count_sentences("好吃。真的好吃!") == 2
    assert count_sentences("One sentence only") == 1


def test_check_constraints_all_keys():
    out = "Selamat pagi, ada meeting hari ini."
    checks = {
        "starts_with": "selamat pagi",
        "must_include": ["meeting"],
        "must_not_include": ["cheap"],
        "max_words": 10,
        "min_words": 3,
        "max_sentences": 1,
    }
    assert all(check_constraints(out, checks).values())
    assert not check_constraints(out, {"max_words": 2})["max_words"]


def test_unknown_check_raises():
    with pytest.raises(ValueError):
        check_constraints("x", {"nope": 1})


def test_chrf_identical_is_one():
    assert chrf("hello world", "hello world") == pytest.approx(1.0)
    assert chrf("zzz", "hello world") < 0.2


def test_aggregate_per_task():
    items = [
        make("intent", "a", "complaint", "i1"),
        make("intent", "b", "praise", "i2"),
        make("instruct", "p", json.dumps({"must_include": ["kopi"]}), "s1"),
        make("normalize", "n", "hello there", "n1"),
    ]
    outputs = {"i1": "complaint", "i2": "inquiry", "s1": "minum kopi", "n1": "hello there"}
    s = aggregate(items, outputs)
    assert s["intent"]["accuracy"] == 0.5
    assert s["instruct"]["pass_rate"] == 1.0
    assert s["normalize"]["chrf"] == pytest.approx(1.0)


def test_intent_reference_must_be_valid_label():
    with pytest.raises(ValueError):
        make("intent", "hi", "angry")

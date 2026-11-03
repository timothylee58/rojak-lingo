from rojak.datagen.contamination import build_index
from rojak.io import load_gold
from rojak.schema import TaskType
from rojak.tasks.prompts import FEWSHOT, build_messages
from rojak.text import ngrams, tokens


def test_fewshot_wraps_three_examples_around_prompt():
    msgs = build_messages(TaskType.intent, "hello?", "fewshot")
    assert [m["role"] for m in msgs] == [
        "system", "user", "assistant", "user", "assistant", "user", "assistant", "user",
    ]
    assert msgs[-1]["content"] == "hello?"
    assert build_messages(TaskType.intent, "hello?")[-1]["content"] == "hello?"


def test_fewshot_examples_share_no_5grams_with_gold():
    # Examples sit inside the evaluated prompt, so even the contamination
    # threshold (0.5) is too loose: they must share no 5-gram with gold at all.
    index = build_index(load_gold())[1]
    for pairs in FEWSHOT.values():
        assert len(pairs) == 3
        for text in [t for pair in pairs for t in pair]:
            shared = [g for g in ngrams(tokens(text), 5) if g in index]
            assert shared == [], f"{text[:60]!r} shares {[' '.join(g) for g in shared]}"

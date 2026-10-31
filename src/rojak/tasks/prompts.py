from ..schema import INTENT_LABELS, TaskType

# Eval and training must build prompts through this one function. If they drift apart,
# the fine-tune is graded on a format it never saw and the comparison is unfair.
SYSTEM: dict[TaskType, str] = {
    TaskType.normalize: (
        "Rewrite the message in clear, standard English. Keep the meaning and tone. "
        "Output only the rewritten message."
    ),
    TaskType.intent: (
        "Classify the intent of the message. Answer with exactly one label from: "
        + ", ".join(INTENT_LABELS)
        + "."
    ),
    TaskType.instruct: "Follow the instruction exactly, including every constraint.",
    TaskType.translate: "Follow the translation instruction. Output only the translation.",
}


def build_messages(task: TaskType, prompt: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM[task]},
        {"role": "user", "content": prompt},
    ]

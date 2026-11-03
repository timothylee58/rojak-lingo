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


def build_messages(task: TaskType, prompt: str, style: str = "zero") -> list[dict[str, str]]:
    if style == "zero":
        return [
            {"role": "system", "content": SYSTEM[task]},
            {"role": "user", "content": prompt},
        ]
    if style == "fewshot":
        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM[task] + " Follow the format of the examples."}
        ]
        for user, assistant in FEWSHOT[task]:
            messages += [
                {"role": "user", "content": user},
                {"role": "assistant", "content": assistant},
            ]
        return messages + [{"role": "user", "content": prompt}]
    raise ValueError(f"unknown prompt style: {style}")


# Hand-written, deliberately disjoint from the gold set (never copy gold items here:
# few-shot examples are shown to evaluated models, gold must stay held out).
# Normalize examples always answer in English to pin the output language.
FEWSHOT: dict[TaskType, list[tuple[str, str]]] = {
    TaskType.normalize: [
        (
            "Aiyo this queue damn long, wait almost one hour already.",
            "This queue is unbelievably long. I have waited almost an hour.",
        ),
        (
            "Saya nak order teh ais satu, tapau.",
            "I would like to order one iced milk tea to take away.",
        ),
        (
            "他讲他明天不用来,叫我cover他的shift。",
            "He said he is not coming tomorrow and asked me to cover his shift.",
        ),
    ],
    TaskType.intent: [
        (
            "Food sampai sejuk and lambat half hour, very disappointed.",
            "complaint",
        ),
        (
            "Terima kasih! Your staff sangat friendly and helpful.",
            "praise",
        ),
        (
            "Boleh tahu tak kedai ni buka sampai pukul berapa?",
            "inquiry",
        ),
    ],
    TaskType.instruct: [
        (
            "In a single English sentence, describe the taste of cendol, using the word 'sweet'.",
            "Cendol tastes sweet with coconut milk and gula melaka.",
        ),
        (
            "Tulis satu ayat tentang hujan, mesti ada perkataan 'payung'.",
            "Jangan lupa bawa payung kerana hujan lebat di luar.",
        ),
        (
            "请用中文评论榴莲的味道,带一个'香'字。",
            "榴莲闻起来很香。",
        ),
    ],
    TaskType.translate: [
        (
            "Translate into English: Tolong cepat sikit, saya dah lambat!",
            "Please hurry up, I am already late!",
        ),
        (
            "Translate into Mandarin (Simplified): Auntie sells curry puffs at the market.",
            "阿姨在巴刹卖咖喱角。",
        ),
        (
            "Translate into Bahasa Malaysia: Switch off the fan, please.",
            "Tolong matikan kipas.",
        ),
    ],
}

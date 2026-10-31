# Rojak-Lingo

An open benchmark and LoRA fine-tune for Malaysian code-switching (English, Bahasa Malaysia, Mandarin, Cantonese, Manglish). Built for the Meta Global AI Developer Hackathon, indie track.

## Why
General LLMs handle mixed-language Malaysian text unevenly, and there is no small, reproducible benchmark for it. This repo measures the gap and tries to close it with a small fine-tune.

## Tasks
| Task | Input | Metric |
|---|---|---|
| normalize | rojak message | chrF vs standard English |
| intent | customer message | accuracy, macro-F1 (complaint / inquiry / praise / request / other) |
| instruct | mixed-language instruction | pass rate on programmatic constraints |
| translate | translation request | chrF |

## Architecture
```
gold set (hand-written, held out) ──────────────┐
                                                ▼
teacher model → generate → verify → dedupe → contamination check → train.clean.jsonl
                                                                         │
                                                              Modal: QLoRA SFT
                                                                         │
 Meta API (Muse Spark) ─┐                                                ▼
 base model endpoint  ──┼─→ eval runner (same prompts, same metrics) → summary/*.json → leaderboard.json
 fine-tuned endpoint  ──┘
```
Eval and training build prompts through one function (`tasks/prompts.py`), so the fine-tune is graded on the format it trained on and the base model is not handicapped.

## Quickstart
```bash
cp .env.example .env            # fill in keys, then export them
make setup
make test
python -m rojak.eval.runner --mock          # offline pipeline check, no API calls
python -m rojak.datagen.generate --mock     # offline datagen check
```

Real run:
```bash
make datagen                    # teacher generates, verifies, dedupes
python -m rojak.datagen.contamination --drop
make train                      # Modal GPU, needs the rojak-secrets Modal secret
make eval && make report
```

## Integrity rules
- Gold items never go into any prompt sent to the teacher.
- Instruct training answers are kept only if they pass their own checks.
- `make check` fails CI if train and gold overlap above the threshold.
- Gold items start as `draft`. Review each one and set `"status": "verified"`; the runner records how many drafts were scored.

## Status
- Tested offline: schema, metrics, dedupe, contamination, generation, runner.
- Not yet run: live Meta API calls, Modal training, endpoint serving. Treat `train/modal_train.py` as untested until the first run.

## Limitations
- One reference per gold item, so chrF undercounts valid paraphrases.
- Gold set is small (target ~300), so report confidence intervals, not just means.
- Synthetic data inherits the teacher's biases and may sound less natural than real chat.

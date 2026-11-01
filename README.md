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

## Serving the fine-tune
One Modal endpoint serves both models with vLLM: `model=meta-llama/Llama-3.1-8B-Instruct` is the base, `model=rojak-v1` applies the LoRA adapter. That keeps the comparison on identical hardware and settings.
```bash
modal secret create rojak-secrets HF_TOKEN=... WANDB_API_KEY=... MODAL_ENDPOINT_KEY=<random string>
make deploy-serve               # prints the endpoint URL
# put the URL + /v1 in BASE_MODEL_URL and FT_MODEL_URL, same key in MODAL_ENDPOINT_KEY
python -m rojak.eval.runner --models base,rojak-ft --limit 5     # smoke test
```
The endpoint scales to zero after 5 idle minutes. First request after idle takes several minutes (model load).

## Leaderboard
Static Next.js site in `web/`, reading `leaderboard.json` at runtime so results can change without a rebuild.
```bash
make eval && make report && make web-data
make web-dev                    # add ?sample to the URL to preview with placeholder data
```
Deploy `web/out` (from `npm run build`) to any static host.

## Integrity rules
- Gold items never go into any prompt sent to the teacher.
- Instruct training answers are kept only if they pass their own checks.
- `make check` fails CI if train and gold overlap above the threshold.
- Gold items start as `draft`. Review each one and set `"status": "verified"`; the runner records how many drafts were scored.

## Status
- Tested offline: schema, metrics, dedupe, contamination, generation, runner. Leaderboard builds and renders (checked at desktop and phone width).
- Import-checked only: `train/modal_train.py`, `train/modal_serve.py`. Not yet run: live Meta API calls, Modal training, endpoint serving. Expect to fix small issues on the first real run (vLLM flags and TRL arguments change between versions).

## Limitations
- One reference per gold item, so chrF undercounts valid paraphrases.
- Gold set is small (target ~300), so report confidence intervals, not just means.
- Synthetic data inherits the teacher's biases and may sound less natural than real chat.

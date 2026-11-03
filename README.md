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
gold set: 300 hand-written items, 75 per task, all verified, held out ──┐
                                                                        ▼
teacher model → generate → verify → dedupe → contamination check → train.clean.jsonl
                                                                         │
                                                             Modal: QLoRA SFT (pinned deps)
                                                                         │
 Meta API (Muse Spark) ─┐                                                 ▼
 base model endpoint  ──┼─→ eval runner (same prompts, same metrics) → summary/*.json → leaderboard.json
 fine-tuned endpoint  ──┤
 few-shot base        ──┘
```
Eval and training build prompts through one function (`tasks/prompts.py`), so the fine-tune is graded on the format it trained on and the base model is not handicapped. The few-shot baseline (`base-fs`, 3 hand-written examples per task, zero 5-grams shared with gold) tests how much of each gap is just prompting.

## Quickstart
```bash
cp .env.example .env            # fill in keys, then export them
make setup
make test
uv run python -m rojak.eval.runner --mock          # offline pipeline check, no API calls
uv run python -m rojak.datagen.generate --mock     # offline datagen check
```

Real run:
```bash
make datagen                    # teacher generates, verifies, dedupes
make check                      # contamination gate (use --drop to write train.clean.jsonl)
make train                      # Modal GPU, needs the rojak-secrets Modal secret
make eval                       # base, few-shot base, fine-tune, reference
make significance               # paired tests per task; CIs, not just means
make report && make web-data
```

## Serving the fine-tune
One Modal endpoint serves both models with vLLM: the base weights answer as the base model id, and the LoRA adapter id applies the fine-tune, so the comparison runs on identical hardware and settings. (CUDA devel image is required — flashinfer JIT needs `nvcc`; context window 8192.)
```bash
modal secret create rojak-secrets HF_TOKEN=... WANDB_API_KEY=... MODAL_ENDPOINT_KEY=<random string>
make deploy-serve               # prints the endpoint URL
# put the URL + /v1 in BASE_MODEL_URL and FT_MODEL_URL, same key in MODAL_ENDPOINT_KEY
uv run python -m rojak.eval.runner --models base,rojak-ft --limit 5     # smoke test
```
The endpoint scales to zero after 5 idle minutes. First request after idle takes several minutes (model load).

## Leaderboard
Static Next.js site in `web/`, reading `leaderboard.json` at runtime so results can change without a rebuild. Shows per-task deltas, a verdict line, best-per-task highlights, and run metadata.
```bash
make eval && make report && make web-data
make web-dev                    # add ?sample to the URL to preview with placeholder data
```
Deploy `web/out` (from `npm run build`) to any static host.

## Latest results (300 gold items)
| Task | base | base + few-shot | rojak-ft (v3) | muse-spark |
|---|---|---|---|---|
| instruct pass rate | 0.773 | 0.880 | 0.773 | 1.000 |
| intent macro-F1 | 0.884 | 0.973 | 0.987 | 0.987 |
| normalize chrF | 0.263 | 0.601 | 0.596 | 0.720 |
| translate chrF | 0.580 | 0.583 | 0.597 | 0.755 |

Nothing distinguishes the fine-tune from a well-prompted base on any task (all pairwise comparisons ns); the fine-tune beats zero-shot base on normalize and intent. See `results/significance.json` for CIs and McNemar p-values.

## Integrity rules
- Gold items never go into any prompt sent to the teacher.
- Instruct training answers are kept only if they pass their own checks.
- Few-shot examples share zero 5-grams with gold (enforced by test).
- `make check` fails CI if train and gold overlap above the threshold.
- Gold items start as `draft`. Each one must be read and corrected before `"status": "verified"`; the runner records how many drafts were scored. A 72-item stratified spot-check (all Cantonese items included) lives in `results/gold-spotcheck.md`.

## Status
- Ran for real: datagen (3,323 clean rows after CJK upsampling), QLoRA training (v1–v3), vLLM serving, full evals of all four models, paired significance, leaderboard (verified in headless Chromium at desktop/tablet/phone).
- Fixed along the way: TRL/transformers API drift (pinned deps, `warmup_steps`), flashinfer `nvcc` requirement, vLLM context window, stale warm containers, tokenizer-truncation retries, few-shot/gold overlap.

## Limitations
- One reference per gold item, so chrF undercounts valid paraphrases.
- n=75 per task: treat gaps of a few points as noise; quote `make significance`, not means.
- The fine-tune still drops CJK `must_include` keywords (12/75 instruct fails); CJK upsampling (v3) halved them but did not clear the bar. Likely cause: training rows drop the checks, so copy-the-keyword supervision stays implicit.
- Teacher, reference model, and several baselines share a model family: cross-family references are still missing.
- Gold "verified" means agent-read, not independent human review. The two corrected items are documented in git history; a native-speaker pass is still the highest-value review.

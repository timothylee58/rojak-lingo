.PHONY: setup test lint gold datagen check train serve deploy-serve eval eval-fewshot significance report web-data web-dev web-build

setup:
	uv sync --extra dev --extra train

test:
	uv run pytest -q

lint:
	uv run ruff check src tests

gold:
	uv run python -m rojak.gold_validate

datagen:
	uv run python -m rojak.datagen.generate

check:
	uv run python -m rojak.datagen.contamination

train:
	uv run modal run src/rojak/train/modal_train.py

serve:
	uv run modal serve src/rojak/train/modal_serve.py

deploy-serve:
	uv run modal deploy src/rojak/train/modal_serve.py

eval:
	uv run python -m rojak.eval.runner --models all

eval-fewshot:
	uv run python -m rojak.eval.runner --models base-fs

significance:
	uv run python -m rojak.eval.significance

report:
	uv run python -m rojak.report.build

web-data:
	cp results/leaderboard.json web/public/leaderboard.json

web-dev:
	cd web && npm install && npm run dev

web-build:
	cd web && npm ci && npm run build

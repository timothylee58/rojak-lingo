.PHONY: setup test lint gold datagen check train eval report web

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

eval:
	uv run python -m rojak.eval.runner --models all

report:
	uv run python -m rojak.report.build

web:
	uv run python -m rojak.report.build && cd web && npm install && npm run build

.PHONY: setup check demo quick full ablate
setup:
	uv sync --locked --extra dev
check:
	uv run ruff check src tests
	uv run ruff format --check src tests
	uv run mypy
	uv run pytest -q
demo:
	uv run pqos demo --config configs/demo.yaml
quick:
	uv run pqos evaluate --config configs/evaluation.yaml --profile quick
full:
	uv run pqos evaluate --config configs/evaluation.yaml --profile full
ablate:
	uv run pqos ablate --config configs/ablation.yaml --profile quick

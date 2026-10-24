.PHONY: format lint typecheck test quality demo

format:
	ruff format .
	ruff check --fix .

lint:
	ruff format --check .
	ruff check .

typecheck:
	mypy

test:
	pytest --cov=pagelens --cov-report=term-missing

quality:
	python scripts/quality.py


demo:
	scripts/demo.sh

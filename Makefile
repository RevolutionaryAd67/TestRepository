.PHONY: run lint typecheck format test dev-install

run:
python -m app

lint:
ruff check app tests

format:
black app tests

typecheck:
mypy app

test:
pytest

dev-install:
pip install -e .[dev]

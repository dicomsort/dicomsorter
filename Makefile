.PHONY: test reformat format-check flake8 lint

test:
	pytest \
		--verbose \
		--cov=dicomsorter \
		--cov-report=html \
		--cov-report=term \
		--cov-report=xml \
		tests

reformat:
	black .
	isort .

format-check:
	black . --check
	isort . --check

flake8:
	flake8 .

type-check:
	mypy

lint: type-check format-check flake8

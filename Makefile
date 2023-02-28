.PHONY: test reformat format-check flake8 lint

test:
	pytest \
		--verbose \
		--cov=dicomsorter \
		--cov-report=html \
		--cov-report=term \
		tests

reformat:
	black .
	isort .

format-check:
	black . --check
	isort . --check

flake8:
	flake8 .

lint: format-check flake8

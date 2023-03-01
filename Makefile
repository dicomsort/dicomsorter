.PHONY: test reformat format-check flake8 lint type-check clean test-release release

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

clean:
	rm -rf dist

dist:
	python setup.py sdist

test-release: clean dist
	twine upload --repository testpypi dist/*

release: clean dist
	twine upload --repository pypi dist/*

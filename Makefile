.PHONY: test

test:
	pytest \
		--verbose \
		--cov=dicomsorter \
		--cov-report=html \
		--cov-report=term \
		tests

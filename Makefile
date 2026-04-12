.PHONY: all build test lint metrics-check clean

STRICT ?= 1

all: build test lint

build:
	STRICT=$(STRICT) bash scripts/build.sh

test:
	STRICT=$(STRICT) bash scripts/test.sh

lint:
	STRICT=$(STRICT) bash scripts/lint.sh

metrics-check:
	python3 scripts/generate_metrics_summary.py --check

clean:
	rm -rf tools/cpp/build
	cd tools/go && go clean
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

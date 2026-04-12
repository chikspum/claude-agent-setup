.PHONY: all build test lint doctor policy-check metrics-check verify clean

STRICT ?= 1

all: build test lint

build:
	STRICT=$(STRICT) bash scripts/build.sh

test:
	STRICT=$(STRICT) bash scripts/test.sh

lint:
	STRICT=$(STRICT) bash scripts/lint.sh

doctor:
	STRICT=$(STRICT) bash scripts/check_toolchain.sh

policy-check:
	python3 scripts/check_artifacts.py
	python3 scripts/check_docs_drift.py

metrics-check:
	python3 scripts/generate_metrics_summary.py --check

verify: doctor policy-check metrics-check build test lint

clean:
	rm -rf tools/cpp/build
	cd tools/go && go clean
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: all build test lint doctor policy-check metrics-check verify handoff delegate clean

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

handoff:
	@if [ -z "$(PLAN)" ]; then echo "PLAN is required, e.g. make handoff PLAN=docs/plans/active/example.md"; exit 1; fi
	bash scripts/run_claude_handoff.sh "$(PLAN)"

delegate:
	@if [ -z "$(GOAL)" ]; then echo "GOAL is required, e.g. make delegate GOAL='update docs'"; exit 1; fi
	python3 scripts/delegate_to_claude.py --goal "$(GOAL)"

clean:
	rm -rf tools/cpp/build
	cd tools/go && go clean
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

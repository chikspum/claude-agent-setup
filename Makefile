.PHONY: all build test lint clean

all: build test lint

# ── Build ────────────────────────────────────────
build: build-python build-go build-cpp

build-python:
	cd tools/python && uv sync

build-go:
	cd tools/go && go build ./...

build-cpp:
	cd tools/cpp && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel

# ── Test ─────────────────────────────────────────
test: test-python test-go test-cpp

test-python:
	cd tools/python && pytest -v

test-go:
	cd tools/go && go test ./... -v

test-cpp:
	cd tools/cpp/build && ctest --output-on-failure

# ── Lint ─────────────────────────────────────────
lint: lint-python lint-go lint-cpp

lint-python:
	cd tools/python && ruff check . && ruff format --check .

lint-go:
	cd tools/go && go vet ./... && gofmt -l .

lint-cpp:
	cd tools/cpp && clang-format --dry-run -Werror *.cpp *.h 2>/dev/null || true

# ── Clean ────────────────────────────────────────
clean:
	rm -rf tools/cpp/build
	cd tools/go && go clean
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# /build

Build all tools across all languages. Report any failures.

Steps:
1. Python: `cd tools/python && uv sync`
2. Go: `cd tools/go && go build ./...`
3. C++: `cd tools/cpp && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel`

If any step fails, stop and report the error. Do not continue to the next step.
After all steps succeed, print a summary: which tools were built and their binary sizes if applicable.

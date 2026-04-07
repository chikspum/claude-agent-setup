# /test

Run all tests across all languages. Report results as a summary table.

Steps:
1. Python: `cd tools/python && pytest -v`
2. Go: `cd tools/go && go test ./... -v`
3. C++: `cd tools/cpp/build && ctest --output-on-failure`

Run all three even if one fails. At the end, print:

| Language | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Python   | ...   | ...    | ...    |
| Go       | ...   | ...    | ...    |
| C++      | ...   | ...    | ...    |

If any tests failed, list the failing test names and their error output.

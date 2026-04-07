# Go Agent

You are the Go agent for the claude-agent-setup project.

## Scope

You own everything under `tools/go/` and all `*.go` files in the repo.
Do not modify Python or C++ files.

## Stack

- Go 1.22+
- Tests: `go test ./...`
- Lint: `golangci-lint run`

## Workflow

```bash
# Build
go build ./...

# Test
go test ./... -v

# Vet
go vet ./...

# Format
gofmt -w .
goimports -w .
```

## Code standards

- Errors must be wrapped: `fmt.Errorf("doing X: %w", err)`
- No `panic` in library code — return errors
- Use `context.Context` as the first arg in all IO-bound functions
- Prefer `slog` for logging (stdlib, Go 1.21+)
- Table-driven tests for all non-trivial functions

## Tool interface pattern

Each tool in `tools/go/` must expose a `Run(ctx context.Context, args Args) (Result, error)` function.

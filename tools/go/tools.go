// Package tools provides the Go tool scaffold.
// Add new tools following the Run(ctx, args) -> (Result, error) pattern.
package tools

import "context"

// Args holds input for a tool invocation.
type Args struct {
	Data    string
	Options map[string]string
}

// Result holds the output of a tool invocation.
type Result struct {
	Output  string
	Success bool
}

// Echo returns the input data unchanged. Useful for testing the tool pipeline.
func Echo(ctx context.Context, args Args) (Result, error) {
	return Result{Output: args.Data, Success: true}, nil
}

// TODO: add your tools here

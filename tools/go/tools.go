// Package tools provides the Go tool scaffold.
// Add new tools following the Run(ctx, args) -> (Result, error) pattern.
package tools

import "context"

// Args holds input for a tool invocation.
type Args struct {
	// Data is the primary input — typically a URL, file path, or raw text
	// depending on the tool.
	Data string
	// Options carries tool-specific key/value configuration. Each tool
	// documents the keys it recognises; unknown keys are silently ignored.
	Options map[string]string
}

// Result holds the output of a tool invocation.
type Result struct {
	// Output is the human-readable (or machine-parseable) result produced by
	// the tool. Format is tool-specific and described in each tool's Run doc.
	Output string
	// Success is true when the tool completed its primary objective without
	// error. A false value alongside a nil error indicates a partial result
	// (e.g. some URLs in a batch failed).
	Success bool
}

// Echo returns the input data unchanged. Useful for testing the tool pipeline.
func Echo(ctx context.Context, args Args) (Result, error) {
	return Result{Output: args.Data, Success: true}, nil
}

// TODO: add your tools here

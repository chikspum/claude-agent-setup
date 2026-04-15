package tools

import (
	"context"
	"testing"
)

func TestEcho(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name       string
		input      string
		wantOutput string
		wantOK     bool
	}{
		{"non-empty input returned unchanged", "hello world", "hello world", true},
		{"empty string returned unchanged", "", "", true},
		{"success is true", "any", "any", true},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := Echo(ctx, Args{Data: tc.input})
			if err != nil {
				t.Fatalf("Echo returned unexpected error: %v", err)
			}
			if got.Output != tc.wantOutput {
				t.Errorf("Output = %q, want %q", got.Output, tc.wantOutput)
			}
			if got.Success != tc.wantOK {
				t.Errorf("Success = %v, want %v", got.Success, tc.wantOK)
			}
		})
	}
}

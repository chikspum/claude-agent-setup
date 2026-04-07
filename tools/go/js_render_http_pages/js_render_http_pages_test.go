package js_render_http_pages_test

import (
	"context"
	"strings"
	"testing"

	tools "github.com/your-org/claude-agent-setup/tools/go"
	jsrender "github.com/your-org/claude-agent-setup/tools/go/js_render_http_pages"
)

func TestRun(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name        string
		args        tools.Args
		wantSuccess bool
		wantContain string
		wantErr     bool
	}{
		{
			name:        "happy path — valid URL",
			args:        tools.Args{Data: "https://example.com"},
			wantSuccess: true,
			wantContain: "https://example.com",
		},
		{
			name:        "happy path — URL with options",
			args:        tools.Args{Data: "https://example.org", Options: map[string]string{"wait_selector": "body"}},
			wantSuccess: true,
			wantContain: "https://example.org",
		},
		{
			name:    "edge case — empty URL returns error",
			args:    tools.Args{Data: ""},
			wantErr: true,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result, err := jsrender.Run(ctx, tc.args)

			if tc.wantErr {
				if err == nil {
					t.Fatalf("expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if result.Success != tc.wantSuccess {
				t.Errorf("Success = %v, want %v", result.Success, tc.wantSuccess)
			}
			if tc.wantContain != "" && !strings.Contains(result.Output, tc.wantContain) {
				t.Errorf("Output %q does not contain %q", result.Output, tc.wantContain)
			}
		})
	}
}

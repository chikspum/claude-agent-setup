package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	tools "github.com/your-org/claude-agent-setup/tools/go"
	jsrender "github.com/your-org/claude-agent-setup/tools/go/js_render_http_pages"
)

func main() {
	url := "https://quotes.toscrape.com/js/"
	if len(os.Args) > 1 {
		url = os.Args[1]
	}

	fmt.Printf("Fetching (JS render): %s\n", url)

	result, err := jsrender.Run(context.Background(), tools.Args{
		Data: url,
		Options: map[string]string{
			"wait_selector": ".quote",
		},
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}

	lines := strings.Split(result.Output, "\n")
	// Print first 5 lines (title + length) then first 30 lines of HTML
	for i, l := range lines {
		if i >= 35 {
			fmt.Printf("... (%d more lines)\n", len(lines)-i)
			break
		}
		fmt.Println(l)
	}
}

package jsfetch_test

import (
	"fmt"
	"log"

	"github.com/your-org/claude-agent-setup/tools/go/jsfetch"
)

func ExampleFetch() {
	result, err := jsfetch.Fetch("https://example.com", &jsfetch.Options{
		WaitSelector: "h1", // wait until <h1> appears in DOM
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(result.Title)
	fmt.Printf("HTML length: %d bytes\n", len(result.HTML))
}

func ExampleFetchMany() {
	urls := []string{
		"https://example.com",
		"https://example.org",
	}

	results, err := jsfetch.FetchMany(urls, nil)
	if err != nil {
		log.Printf("partial error: %v", err)
	}

	for _, r := range results {
		if r != nil {
			fmt.Printf("%s — %s\n", r.URL, r.Title)
		}
	}
}

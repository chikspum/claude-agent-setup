// Package js_render_http_pages renders an HTTP page with full JavaScript execution
// using a headless Chromium browser (via chromedp) and returns the resulting HTML.
//
// Pass the target URL in args.Data.
//
// Supported options (via args.Options):
//   - "wait_selector" — CSS selector to wait for before capturing HTML
//   - "timeout"       — fetch timeout as a Go duration string (default: "30s")
//   - "user_agent"    — override the browser User-Agent header
package js_render_http_pages

import (
	"context"
	"fmt"
	"time"

	"github.com/chromedp/chromedp"

	tools "github.com/your-org/claude-agent-setup/tools/go"
)

// Run fetches the URL in args.Data using a headless Chromium browser, waits for
// JavaScript to finish rendering, and returns the fully-rendered outer HTML.
//
// args.Data must be a non-empty absolute URL (e.g. "https://example.com").
//
// Recognised args.Options keys:
//   - "wait_selector" — CSS selector; waits until the element is visible before
//     capturing HTML. If omitted, waits for document.readyState == "complete".
//   - "timeout"       — Go duration string (e.g. "45s", "2m"). Default: "30s".
//   - "user_agent"    — overrides the browser User-Agent header.
//
// On success, Result.Output is a newline-separated header block followed by the
// full HTML document:
//
//	url: <requested URL>
//	title: <page <title> text>
//	html_length: <N> bytes
//
//	<html>...</html>
//
// Returns a non-nil error if args.Data is empty, the timeout is unparseable,
// or Chromium fails to navigate or render the page.
func Run(ctx context.Context, args tools.Args) (tools.Result, error) {
	if args.Data == "" {
		return tools.Result{}, fmt.Errorf("js_render_http_pages: Data must not be empty (expected a URL)")
	}

	timeout := 30 * time.Second
	if v, ok := args.Options["timeout"]; ok && v != "" {
		d, err := time.ParseDuration(v)
		if err != nil {
			return tools.Result{}, fmt.Errorf("js_render_http_pages: invalid timeout %q: %w", v, err)
		}
		timeout = d
	}

	allocOpts := append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.ExecPath("/usr/bin/chromium-browser"),
		chromedp.Flag("no-sandbox", true),
		chromedp.Flag("disable-gpu", true),
		chromedp.Flag("disable-dev-shm-usage", true),
	)
	if ua, ok := args.Options["user_agent"]; ok && ua != "" {
		allocOpts = append(allocOpts, chromedp.UserAgent(ua))
	}

	allocCtx, cancelAlloc := chromedp.NewExecAllocator(ctx, allocOpts...)
	defer cancelAlloc()

	chromCtx, cancelChrom := chromedp.NewContext(allocCtx)
	defer cancelChrom()

	chromCtx, cancelTimeout := context.WithTimeout(chromCtx, timeout)
	defer cancelTimeout()

	var html, title string

	actions := []chromedp.Action{
		chromedp.Navigate(args.Data),
	}
	if sel, ok := args.Options["wait_selector"]; ok && sel != "" {
		actions = append(actions, chromedp.WaitVisible(sel, chromedp.ByQuery))
	} else {
		actions = append(actions, chromedp.WaitReady("body", chromedp.ByQuery))
	}
	actions = append(actions,
		chromedp.Title(&title),
		chromedp.OuterHTML("html", &html),
	)

	if err := chromedp.Run(chromCtx, actions...); err != nil {
		return tools.Result{}, fmt.Errorf("js_render_http_pages: %w", err)
	}

	output := fmt.Sprintf("url: %s\ntitle: %s\nhtml_length: %d bytes\n\n%s", args.Data, title, len(html), html)
	return tools.Result{Output: output, Success: true}, nil
}

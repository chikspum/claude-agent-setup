// Package jsfetch fetches web documents with full JavaScript rendering
// using the Chrome DevTools Protocol (chromedp).
package jsfetch

import (
	"context"
	"fmt"
	"time"

	"github.com/chromedp/chromedp"
)

// Options controls the fetch behaviour. A nil *Options is valid and uses all
// default values.
type Options struct {
	// Timeout for the entire operation. Default: 30s for Fetch, 60s for FetchMany.
	Timeout time.Duration
	// WaitSelector is a CSS selector to wait for before capturing HTML.
	// If empty, waits until document.readyState == "complete" (body ready).
	WaitSelector string
	// UserAgent overrides the browser User-Agent header. Empty means default.
	UserAgent string
	// Headless runs Chrome without a visible window. Default: true.
	Headless bool
}

// Result holds the fetched document data returned by Fetch and FetchMany.
type Result struct {
	// URL is the originally requested URL (not the final redirected URL).
	URL string
	// HTML is the outer HTML of the fully-rendered document (<html>…</html>).
	HTML string
	// Title is the text content of the page's <title> element.
	Title string
	// StatusCode is the HTTP response status of the main navigation request.
	// Derived from the Navigation Timing API; defaults to 200 when unavailable.
	StatusCode int64
}

// Fetch opens url in a headless Chromium instance, waits for JavaScript to
// finish rendering, and returns the fully-rendered document.
//
// Each call to Fetch spawns a new browser process and a single tab, then tears
// them down on return. For multiple URLs, prefer FetchMany which reuses one
// browser instance across tabs.
//
// Returns an error if the browser cannot be launched, navigation fails, or the
// operation exceeds opts.Timeout.
func Fetch(url string, opts *Options) (*Result, error) {
	if opts == nil {
		opts = &Options{}
	}
	if opts.Timeout == 0 {
		opts.Timeout = 30 * time.Second
	}

	// Build allocator options.
	allocOpts := chromedp.DefaultExecAllocatorOptions[:]
	if !opts.Headless {
		allocOpts = append(allocOpts, chromedp.Flag("headless", false))
	}
	if opts.UserAgent != "" {
		allocOpts = append(allocOpts, chromedp.UserAgent(opts.UserAgent))
	}

	allocCtx, cancelAlloc := chromedp.NewExecAllocator(context.Background(), allocOpts...)
	defer cancelAlloc()

	ctx, cancelCtx := chromedp.NewContext(allocCtx)
	defer cancelCtx()

	ctx, cancelTimeout := context.WithTimeout(ctx, opts.Timeout)
	defer cancelTimeout()

	var result Result
	result.URL = url

	actions := []chromedp.Action{
		chromedp.Navigate(url),
	}

	// Wait strategy: specific selector or full page load.
	if opts.WaitSelector != "" {
		actions = append(actions, chromedp.WaitVisible(opts.WaitSelector, chromedp.ByQuery))
	} else {
		actions = append(actions, chromedp.WaitReady("body", chromedp.ByQuery))
	}

	actions = append(actions,
		chromedp.Title(&result.Title),
		chromedp.OuterHTML("html", &result.HTML),
		chromedp.Evaluate(`window.performance.getEntriesByType("navigation")[0]?.responseStatus ?? 200`,
			&result.StatusCode),
	)

	if err := chromedp.Run(ctx, actions...); err != nil {
		return nil, fmt.Errorf("jsfetch: %w", err)
	}

	return &result, nil
}

// FetchMany fetches multiple URLs concurrently, reusing a single Chromium
// browser process. Each URL is opened in its own tab (up to maxConcurrent=4
// tabs at a time). Results are returned in the same order as urls.
//
// If one or more tabs fail, FetchMany returns the partial results slice
// alongside the first non-nil error. Callers should check each element for nil
// before use.
//
// The total timeout in opts applies to the entire batch, not per-URL.
func FetchMany(urls []string, opts *Options) ([]*Result, error) {
	if opts == nil {
		opts = &Options{}
	}
	if opts.Timeout == 0 {
		opts.Timeout = 60 * time.Second
	}

	allocOpts := chromedp.DefaultExecAllocatorOptions[:]
	if opts.UserAgent != "" {
		allocOpts = append(allocOpts, chromedp.UserAgent(opts.UserAgent))
	}

	allocCtx, cancelAlloc := chromedp.NewExecAllocator(context.Background(), allocOpts...)
	defer cancelAlloc()

	browserCtx, cancelBrowser := chromedp.NewContext(allocCtx)
	defer cancelBrowser()

	ctx, cancelTimeout := context.WithTimeout(browserCtx, opts.Timeout)
	defer cancelTimeout()

	// Launch browser with a blank first tab.
	if err := chromedp.Run(ctx); err != nil {
		return nil, fmt.Errorf("jsfetch: browser start: %w", err)
	}

	results := make([]*Result, len(urls))
	errs := make([]error, len(urls))

	type job struct {
		idx int
		url string
	}

	jobCh := make(chan job, len(urls))
	for i, u := range urls {
		jobCh <- job{i, u}
	}
	close(jobCh)

	// Run tabs concurrently (bounded by semaphore).
	const maxConcurrent = 4
	sem := make(chan struct{}, maxConcurrent)
	done := make(chan struct{}, len(urls))

	for j := range jobCh {
		j := j
		sem <- struct{}{}
		go func() {
			defer func() { <-sem; done <- struct{}{} }()

			// Each tab gets its own context derived from the shared browser.
			tabCtx, cancel := chromedp.NewContext(browserCtx)
			defer cancel()

			var r Result
			r.URL = j.url

			actions := []chromedp.Action{chromedp.Navigate(j.url)}
			if opts.WaitSelector != "" {
				actions = append(actions, chromedp.WaitVisible(opts.WaitSelector, chromedp.ByQuery))
			} else {
				actions = append(actions, chromedp.WaitReady("body", chromedp.ByQuery))
			}
			actions = append(actions,
				chromedp.Title(&r.Title),
				chromedp.OuterHTML("html", &r.HTML),
			)

			if err := chromedp.Run(tabCtx, actions...); err != nil {
				errs[j.idx] = fmt.Errorf("jsfetch %s: %w", j.url, err)
				return
			}
			results[j.idx] = &r
		}()
	}

	for range urls {
		<-done
	}

	// Collect first non-nil error.
	for _, err := range errs {
		if err != nil {
			return results, err
		}
	}
	return results, nil
}

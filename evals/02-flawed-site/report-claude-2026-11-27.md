# Website Audit: http://127.0.0.1:8921 (local test fixture)

- **Date:** 2026-11-27
- **Scope:** Technical SEO, security headers, performance (static indicators), accessibility (static HTML), content quality
- **Pages sampled:** http://127.0.0.1:8921/ (homepage only, as requested)
- **Environment tier:** B

## Summary

The homepage has problems in every audited area: 38 distinct issues (counts are distinct issue types, not instances, per the merged report). The most serious is a password field on a page served over plain HTTP, so credentials would be sent unencrypted. The page also tells search engines not to index it and has no title. Fix transport first (serve over HTTPS), then the indexability blockers, then the header and labelling hygiene below.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 5 |
| Medium | 16 |
| Low | 17 |

## Top priorities

1. Password field on a page served over plain HTTP: anyone on the network path can read submitted credentials; serve the site over HTTPS.
2. Meta robots `noindex, nofollow` on the homepage: the page tells search engines not to index it.
3. Missing `<title>`: the page has no non-empty title.

## Findings

### SEO

### [High] robots.txt disallows the whole site for specific crawlers  (verified)
- Where: http://127.0.0.1:8921 (robots.txt)
- Evidence: agents `["badbot"]`, rule `Disallow: /` (from check_crawl)
- Why it matters: The named crawlers are blocked from every path on the site.
- Fix: If the block is not deliberate, remove the `Disallow: /` rule for those agents from robots.txt.

### [High] Meta robots tells search engines not to index this page  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `<meta name="robots" content="noindex, nofollow">`
- Why it matters: Search engines are instructed to keep this page out of the index and not to follow its links.
- Fix: Remove the meta robots tag, or change it to `index, follow`, on any page that should be findable.

### [High] Page has no non-empty `<title>`  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `titles_found: []` (from check_html)
- Why it matters: The title is the page's primary label in search results and browser tabs (also WCAG 2.4.2).
- Fix: Add one descriptive `<title>` in the page `<head>`.

### [Medium] A JSON-LD block is not valid JSON  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: parse error "Expecting property name enclosed in double quotes: line 1 column 23 (char 22)"; snippet `{ "@type": "Article",`
- Why it matters: Parsers discard malformed structured data, so the block has no effect.
- Fix: Correct the JSON syntax in the JSON-LD block and re-validate it.

### [Medium] No meta description  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: No meta description found by check_html on this page.
- Why it matters: Search engines compose the result snippet themselves when no description is provided.
- Fix: Add a `<meta name="description" content="...">` summarising the page.

### [Medium] Sitemap lists URLs on a different host  (verified)
- Where: http://127.0.0.1:8921 (sitemap)
- Evidence: 1 cross-host URL in the sitemap sample: `http://other.example/x` (from check_crawl)
- Why it matters: A sitemap should list canonical URLs on its own host; foreign URLs are ignored or treated as errors.
- Fix: Remove URLs that are not on this host from the sitemap.

### [Medium] Sampled sitemap URLs that do not return 200 directly  (verified)
- Where: http://127.0.0.1:8921 (sitemap)
- Evidence: 3 of 4 sampled URLs (sampled 4 of 4 total): `http://127.0.0.1:8921/redirect -> 301`, `http://127.0.0.1:8921/missing -> 404`, `http://other.example/x -> RemoteDisconnected: Remote end closed connection without response`
- Why it matters: Sitemap entries should be live, canonical URLs; redirects and 404s waste crawl attention and signal stale maintenance.
- Fix: Update the sitemap to list only the final URLs that return 200.

### [Low] Canonical URL differs from the fetched URL  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: canonical `https://example.com/other`, page URL `http://127.0.0.1:8921/`
- Why it matters: The page declares a different URL as its canonical version; confirm this is intended.
- Fix: If not intended, point the canonical at the page's own URL.

### [Low] More than one `<h1>`  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: H1 texts found: `["One", "Two"]`
- Why it matters: Multiple H1s blur the page's main heading for assistive technology and crawlers.
- Fix: Keep one `<h1>` and demote the other to `<h2>`.

### [Low] Heading levels are skipped  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 occurrence: `h1 to h3 at 'Jump'`
- Why it matters: Skipped levels break the heading outline used for navigation by screen-reader users (WCAG 1.3.1).
- Fix: Use heading levels in order (h1, then h2, then h3).

### [Low] Open Graph tags missing  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Missing: `og:title`, `og:description`, `og:image`
- Why it matters: Shares of the page on social platforms fall back to scraped text and no chosen image.
- Fix: Add the three Open Graph tags with absolute URLs.

### [Low] robots.txt rules may block asset paths  (needs_manual_check)
- Where: http://127.0.0.1:8921 (robots.txt)
- Evidence: `Disallow: /assets/js/`
- Why it matters: If rendering resources sit under the blocked paths, crawlers cannot render pages fully; the script lists rules as written and does not evaluate per-URL crawlability.
- Fix: Verify the blocked paths hold no CSS/JS needed for rendering; if they do, allow those paths.

### Security

### [High] Password field on a page served over HTTP  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_html found a password field on `http://127.0.0.1:8921/`; the page's final URL is plain HTTP.
- Why it matters: Passwords submitted from this page travel unencrypted and can be read or modified in transit.
- Fix: Serve the site over HTTPS and redirect all HTTP traffic to HTTPS; never render password fields on HTTP pages.

### [High] The final URL is served over plain HTTP  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `http://127.0.0.1:8921/` (from check_headers)
- Why it matters: All content and form data on this page are unencrypted in transit.
- Fix: Obtain a TLS certificate, serve the site over HTTPS, and redirect HTTP to HTTPS.

### [Medium] No clickjacking protection on this response  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Neither X-Frame-Options nor CSP frame-ancestors was sent (from check_headers).
- Why it matters: Other sites can embed this page in a frame and overlay it for clickjacking.
- Fix: Send `X-Frame-Options: DENY` (or SAMEORIGIN), or a Content-Security-Policy with `frame-ancestors`.

### [Medium] Cookie without HttpOnly  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Cookie named in check_headers output: `sid`
- Why it matters: Without HttpOnly, page scripts can read the cookie, so a script injection can steal it.
- Fix: Set the `HttpOnly` attribute on the `sid` cookie (and on any session cookie).

### [Medium] No Content-Security-Policy header on this response  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `report_only_present: false`; no CSP header on this response (from check_headers).
- Why it matters: Without a CSP there is no browser-enforced restriction on where scripts and other resources may load from.
- Fix: Add a Content-Security-Policy header, starting from a restrictive default such as `default-src 'self'` and loosening only as needed.

### [Low] Cookie without an explicit SameSite attribute  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Cookie named in check_headers output: `sid`
- Why it matters: The cookie's cross-site sending behaviour is left to browser defaults.
- Fix: Set an explicit `SameSite` attribute (for example `SameSite=Lax`) on the `sid` cookie.

### [Low] Response headers reveal software or version details  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `Server: BaseHTTP/0.6 Python/3.12.3`
- Why it matters: Exact version strings help an attacker match the server against known advisories; this is a lead, not proof of a vulnerability.
- Fix: Remove the version detail from the `Server` header or send a generic value.

### [Low] No Permissions-Policy header  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: No Permissions-Policy header on this response (from check_headers).
- Why it matters: Browser features such as camera, microphone and geolocation are not explicitly restricted for this page.
- Fix: Add a Permissions-Policy header disabling features the page does not use.

### [Low] No Referrer-Policy header  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: No Referrer-Policy header on this response (from check_headers).
- Why it matters: The full page URL can leak to third parties through the Referer header.
- Fix: Add `Referrer-Policy: strict-origin-when-cross-origin` (or stricter).

### [Low] No security.txt at the standard location  (verified)
- Where: http://127.0.0.1:8921
- Evidence: security.txt request returned status 404 (from check_crawl). The script's message notes this is optional best practice.
- Why it matters: Security researchers have no published contact route for reporting problems.
- Fix: Publish a security.txt at `/.well-known/security.txt` with a contact address.

### [Low] X-Content-Type-Options: nosniff not present  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Header not present on this response (from check_headers).
- Why it matters: Browsers may MIME-sniff responses and treat content as a different type than declared.
- Fix: Send `X-Content-Type-Options: nosniff`.

### Performance

Core Web Vitals were **not measured**: this is a Tier B environment and `check_rendered.py` (Tier C) was not run. The two findings below are static indicators from the HTML, not metrics.

### [Medium] External script in `<head>` without async/defer/module  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 render-blocking script: `/head-blocking.js`
- Why it matters: A synchronous script in the head delays first rendering until it loads and executes.
- Fix: Add `defer` (or `async` where order does not matter) to the script tag, or move it to the end of the body.

### [Low] Images without width and height attributes  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 2 images: `<img src="/a.png">`, `<img src="/b.png" alt="">`
- Why it matters: Without dimensions the browser cannot reserve space, so content shifts as images load (layout shift risk).
- Fix: Add accurate `width` and `height` attributes to each image.

### Accessibility

### [Medium] Button with no accessible name  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 button: `<button>`
- Why it matters: Screen-reader users hear an unlabelled button and cannot tell what it does (WCAG 4.1.2).
- Fix: Give the button visible text or an `aria-label`.

### [Medium] `<html>` has no lang attribute  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: No `lang` attribute found by check_html.
- Why it matters: Screen readers cannot select the correct pronunciation without a declared language (WCAG 3.1.1).
- Fix: Add the page's language, for example `<html lang="en">`.

### [Medium] Image without an alt attribute  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 image: `<img src="/a.png">`
- Why it matters: Without alt text the image is invisible or announced by filename to screen-reader users (WCAG 1.1.1).
- Fix: Add descriptive `alt` text, or `alt=""` if the image is purely decorative.

### [Medium] Form controls without a label  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 2 controls: `<input type="text" name="q" placeholder="Search">`, `<input type="password" id="pw">` (a placeholder does not count as a label)
- Why it matters: Unlabelled controls are not announced properly and their purpose is unclear (WCAG 1.3.1, 3.3.2, 4.1.2).
- Fix: Associate a `<label>` with each control (or use `aria-label`).

### [Medium] Link with no accessible name  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 link: `<a href="/good">`
- Why it matters: A link with no text, aria-label, title or image alt is announced as a bare URL or nothing (WCAG 2.4.4, 4.1.2).
- Fix: Add descriptive link text.

### [Medium] Viewport meta restricts pinch zoom  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `width=device-width, user-scalable=no`
- Why it matters: Disabling zoom blocks low-vision users from enlarging the page (WCAG 1.4.4).
- Fix: Remove `user-scalable=no` from the viewport meta.

### [Low] No `<main>` landmark in the static HTML  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: No `<main>` or role=main found by check_html.
- Why it matters: Landmarks let assistive-technology users jump straight to the primary content (WCAG 1.3.1, 2.4.1).
- Fix: Wrap the primary content in a `<main>` element.

### Content

### [Medium] Placeholder-style text in visible content  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 occurrence; example from check_html: "o Broken Redirects Chain mail Lorem ipsum dolor sit amet. © 2019 Exampl"
- Why it matters: Lorem ipsum placeholder copy on a live page is unfinished content presented to visitors.
- Fix: Replace the placeholder text with the real copy.

### [Medium] Broken link  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 broken link: `http://127.0.0.1:8921/missing -> 404` (from check_links)
- Why it matters: Visitors and crawlers following the link reach an error page.
- Fix: Point the link at the correct URL or remove it.

### [Low] Outdated copyright year  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Latest copyright year found: 2019; the audit scripts ran in 2026.
- Why it matters: A stale copyright line signals an unmaintained page.
- Fix: Update the copyright year (or generate it automatically).

### [Low] Little visible text in the static HTML  (likely)
- Where: http://127.0.0.1:8921/
- Evidence: `visible_words: 15` (from check_html). JavaScript was not executed, so content added client-side is not seen; judge against the page's purpose.
- Why it matters: If the static HTML is all there is, the page carries very little readable content.
- Fix: If the page is meant to carry content, publish it in the HTML; if it is a functional page, no change is needed.

### [Low] Link goes through two or more redirects  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 chain: `http://127.0.0.1:8921/old -> http://127.0.0.1:8921/redirect -> http://127.0.0.1:8921/good`
- Why it matters: Each extra redirect adds latency and a point of failure.
- Fix: Point the link directly at `http://127.0.0.1:8921/good`.

### [Low] Link points at a redirecting URL  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: 1 link: `http://127.0.0.1:8921/redirect -> http://127.0.0.1:8921/good`
- Why it matters: The link could point at the final URL directly.
- Fix: Update the link target to `http://127.0.0.1:8921/good`.

## What was not checked

| Area | Check | Reason |
|------|-------|--------|
| Performance | Core Web Vitals (LCP, INP, CLS) | Not measured: Tier B environment, `check_rendered.py` (Tier C, Lighthouse) was not run |
| Accessibility | Rendered checks: colour contrast, focus visibility, keyboard use and traps, reflow | Need a rendered browser (Tier C); the static script does not check these |
| Security | TLS certificate details | The site is served over plain HTTP, so there is no certificate to inspect |
| All areas | Pages other than the homepage | Scope was the homepage only, as requested |
| Content / SEO | JavaScript-rendered content | JavaScript was not executed; content added client-side is not seen |

Automated and static audits only cover part of what matters. Contrast, keyboard use, real-user performance, and anything behind a login need manual or tool-assisted testing.

Notes on method: the merged report's `not_checked` list was empty for the four checks that ran (crawl, headers, HTML, links). The audit environment has a proxy configured (per `detect_env.py`); the target is plain HTTP on loopback, so no TLS properties were measured, and header findings above describe the response received on this network path ("missing" means missing in that response, not necessarily absent site-wide).

## Suggested next steps

- [ ] Serve the site over HTTPS with an HTTP-to-HTTPS redirect, so the password field is never on an HTTP page
- [ ] Remove `noindex, nofollow` from the homepage and add a `<title>` and meta description
- [ ] Clean up robots.txt and the sitemap: review the `Disallow: /` block for specific crawlers, and list only same-host URLs that return 200
- [ ] Add the missing response headers (Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, clickjacking protection) and set HttpOnly and SameSite on the `sid` cookie
- [ ] Label the form controls, name the empty button and link, add alt text and image dimensions, restore pinch zoom, and add a `<main>` landmark
- [ ] Fix the broken `/missing` link, point redirecting links at their final URLs, and replace the placeholder text
- [ ] Re-run the audit after changes to confirm

# Website Audit: http://127.0.0.1:8923

- **Date:** 2026-11-27
- **Scope:** Crawl files (robots.txt, sitemap, security.txt) and the homepage's transport and response headers. On-page SEO, accessibility, content and link checks were attempted but the target refused every page request (HTTP 403), so those areas are reported as not checked.
- **Pages sampled:** http://127.0.0.1:8923/ (homepage; the only page requested — it answered 403, and no other page could be observed)
- **Environment tier:** B

## Summary

This target refuses almost everything: of the requests the audit made, only robots.txt was served (200); the homepage, /sitemap.xml and /.well-known/security.txt all answered 403. The one file that is served, robots.txt, disallows the whole site for all crawlers, which is the single most important finding. The checks that could run produced 10 distinct issues (1 critical, 1 high, 2 medium, 6 low), all from the crawl files and from the headers of the single 403 response; because no page content was ever served, on-page SEO, accessibility, content, performance and link checks could not be performed at all.

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 1 |
| Medium | 2 |
| Low | 6 |

## Top priorities

1. robots.txt disallows the whole site for all crawlers (Critical) — if this origin is meant to be crawled or indexed, nothing else matters until this is changed.
2. The homepage is served over plain HTTP (High) — no HTTPS on the final URL.
3. No Content-Security-Policy and no clickjacking protection on the observed response (Medium ×2).

## Findings

### SEO

### [Critical] robots.txt disallows the whole site  (verified)
- Where: site-wide (http://127.0.0.1:8923/robots.txt)
- Evidence: `check_crawl.py` fetched robots.txt with status 200 and reports agents `["*"]` with rule `"Disallow: /"`; the script's message: "robots.txt disallows the whole site for all crawlers."
- Why it matters: Crawlers that honour robots.txt will not crawl any page on this origin.
- Fix: If the site is meant to be crawled, remove the `Disallow: /` rule for `User-agent: *` or replace it with rules that only block the paths that should stay private.

### [Low] No sitemap declared in robots.txt and none found at /sitemap.xml  (likely)
- Where: site-wide (http://127.0.0.1:8923)
- Evidence: `check_crawl.py` reports `sitemap_directives: []` in robots.txt, and its request to http://127.0.0.1:8923/sitemap.xml returned status 403. The script's message: "No sitemap declared in robots.txt and none found at /sitemap.xml." Because the sitemap request was refused with 403 rather than answered 404, this is labelled likely, not verified: a sitemap the server refuses to show cannot be told apart from one that does not exist.
- Why it matters: A sitemap is the standard way to tell crawlers which URLs exist; without one, discovery depends on links alone.
- Fix: Serve a sitemap at a stable URL with a 200 response and declare it in robots.txt with a `Sitemap:` line.

On-page SEO (title, meta description, canonical, headings, Open Graph, JSON-LD) was **not checked**: `check_html.py` returned `"status": "not_checked"` for the homepage (see "What was not checked").

### Security

All header findings below were measured on one response: the homepage's 403 response. A header reported missing means missing in that response; whether this site's normal pages send these headers could not be observed, because no page was ever served.

### [High] The final URL is served over plain HTTP  (verified)
- Where: http://127.0.0.1:8923/
- Evidence: `check_headers.py` reports the final URL as `http://127.0.0.1:8923/` with the message "The final URL is served over plain HTTP." Its TLS check was not performed: `"checked": false, "reason": "final URL is not https"`.
- Why it matters: Traffic to and from the page is unencrypted and can be read or modified in transit.
- Fix: Serve the site over HTTPS and redirect the HTTP version to the HTTPS version.

### [Medium] No Content-Security-Policy header on this response  (verified)
- Where: http://127.0.0.1:8923/ (403 response)
- Evidence: `check_headers.py` security header measurement: `"content-security-policy": {"present": false, "value": null}`, and no CSP report-only header either (`"report_only_present": false`).
- Why it matters: Without a CSP, the browser applies no extra restriction on where scripts and other resources may load from if a page is ever compromised.
- Fix: Send a `Content-Security-Policy` header, starting from a restrictive policy such as `default-src 'self'` and widening it only for sources the site actually uses.

### [Medium] Neither X-Frame-Options nor CSP frame-ancestors was sent  (verified)
- Where: http://127.0.0.1:8923/ (403 response)
- Evidence: `check_headers.py` reports `"x-frame-options": null` and no CSP (above); its message: "Neither X-Frame-Options nor CSP frame-ancestors was sent."
- Why it matters: Other sites can embed this site's pages in a frame, which is the precondition for clickjacking.
- Fix: Send `X-Frame-Options: DENY` (or `SAMEORIGIN` if the site frames its own pages), or a CSP `frame-ancestors` directive.

### [Low] X-Content-Type-Options: nosniff not present  (verified)
- Where: http://127.0.0.1:8923/ (403 response)
- Evidence: `check_headers.py` measurement: `"x-content-type-options": null`; message: "X-Content-Type-Options: nosniff not present."
- Why it matters: Browsers may MIME-sniff responses and treat content as a different type than the server declared.
- Fix: Send `X-Content-Type-Options: nosniff`.

### [Low] No Referrer-Policy header  (verified)
- Where: http://127.0.0.1:8923/ (403 response)
- Evidence: `check_headers.py` measurement: `"referrer-policy": null`; message: "No Referrer-Policy header."
- Why it matters: The browser default decides how much of a URL is sent as the Referer to other sites, which can leak path details.
- Fix: Send a `Referrer-Policy` header, for example `strict-origin-when-cross-origin`.

### [Low] No Permissions-Policy header  (verified)
- Where: http://127.0.0.1:8923/ (403 response)
- Evidence: `check_headers.py` measurement: `"permissions-policy": null`; message: "No Permissions-Policy header."
- Why it matters: Powerful browser features stay available to the page and anything embedded in it unless a policy restricts them.
- Fix: Send a `Permissions-Policy` header that disables the features the site does not use.

### [Low] Response headers reveal software or version details  (verified)
- Where: http://127.0.0.1:8923/ (403 response)
- Evidence: The response's `Server` header, as quoted by `check_headers.py`: `"BaseHTTP/0.6 Python/3.12.3"`.
- Why it matters: Exact software and version strings give an attacker a head start in matching the server to known issues. (This is a lead, not proof of any vulnerability.)
- Fix: Reduce the `Server` header to a generic value or suppress the version detail.

### [Low] No security.txt at the standard location  (verified)
- Where: http://127.0.0.1:8923/.well-known/security.txt
- Evidence: `check_crawl.py` requested the standard location and recorded `"status": 403`; its message: "No security.txt at the standard location (optional best practice)."
- Why it matters: There is no published contact for reporting security problems with this site. This is optional best practice, and here it is also consistent with the server refusing the request.
- Fix: Publish a security.txt with a contact address at /.well-known/security.txt and answer it with 200.

Cookies: the one observed response set no cookies (`"cookies": []` in `check_headers.py`), so there were no cookie attributes to assess.

### Performance

Not checked. The static performance signals come from `check_html.py`, which returned `"status": "not_checked"` because the homepage answered HTTP 403 with a `text/plain` body. Core Web Vitals and rendered checks (`check_rendered.py`) are Tier C and this environment is Tier B, so they were not run. The only timing measured is `time_to_headers_ms: 3` for the single header request, which the script itself notes is "single request from this machine; not a performance score", so no performance conclusion is drawn from it.

### Accessibility

Not checked. Static accessibility signals come from `check_html.py` (not checked, HTTP 403) and rendered accessibility including contrast comes from `check_rendered.py` (Tier C, not run at Tier B). No HTML was ever served, so there was nothing to assess.

### Content

Not checked. Content checks (readability signals, thin or duplicate content) are part of `check_html.py`, which returned `"status": "not_checked"` for the homepage (HTTP 403, `text/plain` body of 9 bytes per the response's `Content-Length: 9`). There is no page content to evaluate.

## What was not checked

| Area | Check | Reason |
|------|-------|--------|
| SEO | On-page checks: title, meta description, canonical, headings, Open Graph, JSON-LD (`check_html.py`) | Homepage answered HTTP 403; the script returned `"status": "not_checked"` with errors "HTTP 403" and "not HTML (content-type: text/plain)" |
| Links | Status codes and redirect chains of links on the page (`check_links.py`) | Homepage answered HTTP 403; the script returned `"status": "not_checked"` with error "HTTP 403" |
| Performance | Core Web Vitals, lab (`check_rendered.py`) | Tier C check; this environment is Tier B, so it was not run |
| Performance | Static performance signals (`check_html.py`) | Not checked, HTTP 403 (see above) |
| Accessibility | Rendered accessibility and contrast (`check_rendered.py`) | Tier C check; not run at Tier B |
| Accessibility | Static accessibility signals (`check_html.py`) | Not checked, HTTP 403 (see above) |
| Content | Content quality signals (`check_html.py`) | Not checked, HTTP 403 (see above) |
| Security | TLS certificate and HTTPS behaviour | The final URL is plain HTTP; `check_headers.py` reports TLS `"checked": false` with reason "final URL is not https" |
| All areas | Every page other than the homepage | Only the homepage was sampled; the server refused the page request that was made, and no other page was observed |

Notes on the evidence: this audit ran in an environment with proxy variables set (`detect_env.py` reports `proxy_variables_set: ["all_proxy", "http_proxy", "https_proxy"]`, and `check_headers.py` flags `tls_interception_suspected: true`). The target here is plain HTTP on the same machine, and no TLS was involved, but in general, header and certificate observations in such an environment describe what this machine's network path presents and certificate details would be unconfirmed. Separately, all header findings in this report come from a single 403 response, per the script's own caveat: "Headers are from one response; other paths, methods or user agents may differ."

Automated and static audits only cover part of what matters. Contrast, keyboard use, real-user performance, and anything behind a login need manual or tool-assisted testing.

## Suggested next steps

- [ ] Decide whether this origin should refuse everything: if it should be crawled or used, remove the `Disallow: /` rule from robots.txt and stop answering page requests with 403
- [ ] Serve the site over HTTPS and redirect HTTP to HTTPS
- [ ] Add the missing response headers on real pages: Content-Security-Policy (with frame-ancestors or X-Frame-Options), X-Content-Type-Options: nosniff, Referrer-Policy, Permissions-Policy
- [ ] Reduce the version detail in the Server header
- [ ] Publish a sitemap and a /.well-known/security.txt, both answered with 200
- [ ] Re-run the audit after changes to confirm — in particular once pages are served with 200, so the on-page SEO, accessibility, content and link checks can actually run

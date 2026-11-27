# Website Audit: Shopfront — SPA fixture (http://127.0.0.1:8922)

- **Date:** 2026-11-27
- **Scope:** Technical SEO, security headers, performance (static indicators only), accessibility (static HTML only), and content
- **Pages sampled:** http://127.0.0.1:8922/ (homepage only — no other pages were discoverable: the sitemap returned 404 and the static HTML contains no links)
- **Environment tier:** B (detect_env reached the target directly, status 200; rendered/Lighthouse checks were attempted and returned not_checked, see "What was not checked")
- **Audit environment note:** detect_env reported proxy variables set in this environment (`all_proxy`, `http_proxy`, `https_proxy`). The target is plain HTTP on loopback, so no TLS measurements exist in this audit.

## Summary

The target is a client-rendered single-page app: the static HTML is a 352-byte shell (title "Shopfront — SPA fixture") whose content is added by JavaScript, which these checks do not execute. The merged checks found 14 distinct issues (0 critical, 1 high, 3 medium, 10 low), most of them missing response security headers on the homepage response, plus the page being served over plain HTTP. The single most important thing to fix first is serving the site over HTTPS. Because JavaScript was not executed and Lighthouse was unavailable, the rendered app (its real headings, landmarks, links, and text), Core Web Vitals, and color contrast were not checked; several findings below describe the static shell exactly as their script messages state, and the rendered output may differ.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 1 |
| Medium | 3 |
| Low | 10 |

## Top priorities

1. Serve the site over HTTPS — the final URL is plain HTTP (High).
2. Add clickjacking protection — neither X-Frame-Options nor CSP frame-ancestors was sent (Medium).
3. Add a Content-Security-Policy header — none was sent on the homepage response (Medium).
4. Give the page an `<h1>` — none exists in the static HTML, and the rendered equivalent was not checked (Medium).

## Findings

### SEO

#### [Medium] No `<h1>` in the static HTML (verified)
- Where: http://127.0.0.1:8922/
- Evidence: check_html measured `h1: []`; message: "No <h1> found in the static HTML."
- Why it matters: A page should expose one meaningful heading stating its topic; in the static HTML there is none for crawlers or assistive technology that read the unrendered page.
- Fix: Make sure the page has exactly one meaningful `<h1>`. If the app adds it client-side, confirm it in the rendered DOM (rendered checks were not available in this run).

#### [Low] No sitemap found (likely)
- Where: site-wide (http://127.0.0.1:8922)
- Evidence: check_crawl measured robots.txt with `sitemap_directives: []` and GET http://127.0.0.1:8922/sitemap.xml returned status 404; message: "No sitemap declared in robots.txt and none found at /sitemap.xml."
- Why it matters: A sitemap gives crawlers the list of canonical URLs to index; without one they must discover pages by following links.
- Fix: Publish a sitemap listing the canonical, indexable URLs and add a `Sitemap:` line to robots.txt.

#### [Low] No canonical link (verified)
- Where: http://127.0.0.1:8922/
- Evidence: check_html measured `canonical: []`; message: "No canonical link."
- Why it matters: Without a canonical, the same content reachable at several URLs has no declared preferred version.
- Fix: Add a self-referencing `<link rel="canonical">` with the page's absolute preferred URL.

#### [Low] Open Graph tags missing (verified)
- Where: http://127.0.0.1:8922/
- Evidence: check_html measured `og:title`, `og:description`, and `og:image` all false; the issue's evidence lists "og:title", "og:description", "og:image".
- Why it matters: Shares of the page on social and chat platforms fall back to scraped text with no chosen title, description, or image.
- Fix: Add `og:title`, `og:description`, and `og:image` meta tags with absolute URLs.

Checked with no issues: the title is present ("Shopfront — SPA fixture", 23 characters) and a meta description is present (57 characters), per check_html measurements; robots.txt exists (status 200) and its only group (`*`) allows `/`, per check_crawl.

### Security

#### [High] Served over plain HTTP (verified)
- Where: http://127.0.0.1:8922/
- Evidence: check_headers message: "The final URL is served over plain HTTP." The redirect chain is a single 200 response at the http:// URL, and TLS was not checked because the "final URL is not https".
- Why it matters: Plain HTTP sends page content and any user input unencrypted and unprotected against modification in transit.
- Fix: Serve the site over HTTPS and redirect the HTTP version to it. (Context: this target is a loopback test fixture, so nothing leaves this machine today; the finding describes the serving setup exactly as measured, and it is the first thing to change before any public deployment.)

#### [Medium] No clickjacking protection (verified)
- Where: http://127.0.0.1:8922/ (this response)
- Evidence: check_headers message: "Neither X-Frame-Options nor CSP frame-ancestors was sent." The measurements show `x-frame-options: null`.
- Why it matters: Without frame protection, another site can embed this page in a frame and overlay it to trick users into clicking.
- Fix: Add `frame-ancestors 'self'` to a Content-Security-Policy header, or send `X-Frame-Options: SAMEORIGIN`.

#### [Medium] No Content-Security-Policy header (verified)
- Where: http://127.0.0.1:8922/ (this response)
- Evidence: check_headers measured `content-security-policy` as `present: false`, with no report-only policy either (`report_only_present: false`); message: "No Content-Security-Policy header on this response."
- Why it matters: Without a CSP, any script that reaches the page runs with full access to it.
- Fix: Send a Content-Security-Policy header that allows only the origins the app actually uses.

#### [Low] X-Content-Type-Options missing (verified)
- Where: http://127.0.0.1:8922/ (this response)
- Evidence: check_headers message: "X-Content-Type-Options: nosniff not present."
- Why it matters: Without `nosniff`, browsers may guess a response's content type and treat it as something more dangerous than declared.
- Fix: Send `X-Content-Type-Options: nosniff`.

#### [Low] No Referrer-Policy header (verified)
- Where: http://127.0.0.1:8922/ (this response)
- Evidence: check_headers message: "No Referrer-Policy header."
- Why it matters: Without a policy, browsers apply their default and may send more of the page URL to other sites than intended.
- Fix: Send a Referrer-Policy header, for example `strict-origin-when-cross-origin`.

#### [Low] No Permissions-Policy header (verified)
- Where: http://127.0.0.1:8922/ (this response)
- Evidence: check_headers message: "No Permissions-Policy header."
- Why it matters: Without a policy, browser features such as camera, microphone, and geolocation stay available to the page and its embeds by default.
- Fix: Send a Permissions-Policy header that disables the browser features the site does not use.

#### [Low] Server header reveals software and version (verified)
- Where: http://127.0.0.1:8922/ (this response)
- Evidence: check_headers disclosure evidence: `Server: BaseHTTP/0.6 Python/3.12.3`. A version string is a lead, not proof of any vulnerability.
- Why it matters: Exact software versions help an attacker choose which known issues to try first.
- Fix: Suppress the `Server` header or reduce it to a generic value without version details.

#### [Low] No security.txt (verified)
- Where: site-wide (http://127.0.0.1:8922)
- Evidence: check_crawl measured GET http://127.0.0.1:8922/.well-known/security.txt returning status 404; message: "No security.txt at the standard location (optional best practice)."
- Why it matters: Without a published contact, people who find a security problem have no obvious way to report it.
- Fix: Publish a security.txt at `/.well-known/security.txt` with a contact for security reports.

Checked with no issues: no cookies were set on the homepage response (check_headers measured `cookies: []`), so there are no cookie flags to fault.

### Performance

No performance issues were raised by the checks performed. Static indicators from one fetch of the homepage (check_html; these are indicators, not Core Web Vitals): HTML 352 bytes decoded and 352 bytes on the wire, no content encoding, 1 external script, 0 stylesheets, 0 images; check_headers measured no Cache-Control header on the HTML response. Core Web Vitals were not measured — see "What was not checked".

### Accessibility

#### [Low] No `<main>` landmark in the static HTML (verified)
- Where: http://127.0.0.1:8922/
- Evidence: check_html measured `has_main_landmark: false`; message: "No <main> or role=main in the static HTML." (WCAG 1.3.1, 2.4.1)
- Why it matters: A main landmark lets keyboard and screen-reader users jump straight to the page's primary content.
- Fix: Wrap the app's primary content in a `<main>` element (or `role="main"`) in the rendered output.

Checked with no issues in the static HTML: `<html lang="en">` is present, and the viewport meta is "width=device-width, initial-scale=1", which does not disable zoom. The static HTML contains 0 images and 0 form controls, so there were no alt-text or labelling instances to check. Contrast, focus visibility, keyboard use, and reflow were not checked — see "What was not checked".

### Content

#### [Low] Little visible text in the static HTML (likely)
- Where: http://127.0.0.1:8922/
- Evidence: check_html counted `visible_words: 4`; message: "Little visible text in the static HTML; judge against the page's purpose."
- Why it matters: Anything that reads the page without running JavaScript (some crawlers, link previews, text-only tools) sees an almost empty page; the app's real text is added client-side and was not seen by these checks.
- Fix: No change is required if the rendered app carries the content; if the page must work without JavaScript, render the main content server-side. Verify against the rendered page, which was not checked here.

Links: check_links ran on the homepage and found 0 links in the static HTML (`unique_links_found: 0`, `checked: 0`), so there were no broken links or redirect chains to report; links the app adds after rendering were not checked.

## What was not checked

| Area | Check | Reason |
|------|-------|--------|
| Performance | Core Web Vitals (LCP, INP, CLS) | check_rendered returned `not_checked`: "Lighthouse not found (looked at --lighthouse-bin, $LIGHTHOUSE_BIN, PATH)" |
| Accessibility | Rendered accessibility audits, including color contrast | Same as above: Lighthouse is unavailable in this environment, so the run stayed at Tier B |
| Accessibility | Contrast, focus visibility, keyboard traps and tab order, reflow | Not covered by the static HTML check; they need a rendered browser |
| All areas | The rendered page: headings, landmarks, links, images, and text the app adds with JavaScript | No script in this run executes JavaScript; the static checks saw the app shell only |
| Security | TLS certificate and HTTPS behaviour | The final URL is not https, so check_headers did not check TLS |
| SEO | Indexation status in search engines, hreflang reciprocity | Not covered by the skill's scripts |

Automated and static audits only cover part of what matters. Contrast, keyboard use, real-user performance, and anything behind a login need manual or tool-assisted testing.

## Suggested next steps

- [ ] Serve the site over HTTPS and redirect HTTP to it
- [ ] Add the missing response headers: Content-Security-Policy (including frame-ancestors), X-Content-Type-Options: nosniff, Referrer-Policy, Permissions-Policy
- [ ] Confirm the rendered page has exactly one `<h1>` and a `<main>` landmark; add them if it does not
- [ ] Add a canonical link and Open Graph tags to the page head
- [ ] Publish a sitemap and reference it in robots.txt; optionally add /.well-known/security.txt
- [ ] Re-run the audit after changes to confirm (ideally with Lighthouse available, so the rendered page and Core Web Vitals are checked too)

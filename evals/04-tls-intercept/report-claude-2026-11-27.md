# Website Audit: http://127.0.0.1:8921 (local test fixture)

- **Date:** 2026-11-27
- **Scope:** Technical SEO, security headers, performance (static signals), accessibility (static signals), content
- **Pages sampled:** http://127.0.0.1:8921/ (homepage only, as requested)
- **Environment tier:** B

## Summary

The homepage carries defects in every audited area: 38 distinct issues in the merged script output, including a password field on a page served over plain HTTP, a `noindex` directive and no `<title>` on the homepage, and a robots.txt rule that disallows the whole site for specific crawlers. The single most important fix is transport: the page is served over HTTP while asking for a password. One environment caveat applies to this whole run: it was executed behind a TLS-inspecting proxy (`tls_interception_suspected: true` in the check_headers output, with proxy variables set), so TLS certificate details are **unconfirmed**; for this target TLS was not checked at all because the final URL is plain HTTP. Re-run from a network without TLS inspection to confirm anything TLS-related.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 5 |
| Medium | 16 |
| Low | 17 |

## Top priorities

1. Password field on an HTTP page (and the site is served over plain HTTP): credentials would travel unencrypted.
2. Homepage tells search engines not to index it (`noindex, nofollow`) and has no `<title>`.
3. robots.txt disallows the whole site for specific crawlers (`Disallow: /` for `badbot`), and the sitemap lists URLs that redirect, 404, or sit on another host.

## Findings

### SEO

### [High] robots.txt disallows the whole site for specific crawlers  (verified)
- Where: http://127.0.0.1:8921 (robots.txt)
- Evidence: check_crawl output: agents `["badbot"]`, rule `Disallow: /`
- Why it matters: Any crawler matching that agent name is blocked from the entire site.
- Fix: Remove or narrow the `Disallow: /` rule for that user-agent group in robots.txt, if blocking it everywhere is not intended.

### [High] Homepage tells search engines not to index it  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `<meta name="robots" content="noindex, nofollow">`
- Why it matters: Search engines are instructed to keep this page out of the index and not follow its links.
- Fix: Remove the meta robots tag, or change it to `index, follow`, if the page is meant to be found.

### [High] Page has no title  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_html output: `titles_found: []` (no non-empty `<title>`)
- Why it matters: The title is the page's primary label in search results and browser tabs; this page has none.
- Fix: Add a unique, descriptive `<title>` to the page.

### [Medium] Sitemap lists URLs that do not return 200  (verified)
- Where: http://127.0.0.1:8921/sitemap.xml
- Evidence: 3 of 4 sampled sitemap URLs did not return 200 directly: `http://127.0.0.1:8921/redirect -> 301`, `http://127.0.0.1:8921/missing -> 404`, `http://other.example/x -> RemoteDisconnected`. The sitemap itself exists: check_crawl fetched it with status 200 (urlset, 4 entries), and robots.txt declares it.
- Why it matters: A sitemap should list canonical URLs that respond 200; redirects and errors waste crawl attention and signal stale maintenance.
- Fix: Update the sitemap to list only the final, same-host URLs that return 200.

### [Medium] Sitemap lists a URL on a different host  (verified)
- Where: http://127.0.0.1:8921/sitemap.xml
- Evidence: `http://other.example/x` (count 1)
- Why it matters: Sitemaps are only processed for URLs on the host the sitemap belongs to; cross-host entries are ignored and suggest a configuration error.
- Fix: Remove cross-host URLs from the sitemap.

### [Medium] No meta description  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_html reports no meta description on the page.
- Why it matters: Search engines will assemble the result snippet from page text instead of a written description.
- Fix: Add a `<meta name="description">` with a concise summary of the page.

### [Medium] JSON-LD block is not valid JSON  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Parse error `Expecting property name enclosed in double quotes: line 1 column 23 (char 22)`; snippet begins `{ "@type": "Article",`
- Why it matters: Structured data that does not parse is discarded by consumers of JSON-LD.
- Fix: Correct the JSON syntax in the JSON-LD block and validate it.

### [Low] Canonical URL differs from the fetched URL  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: canonical `https://example.com/other`, page URL `http://127.0.0.1:8921/`
- Why it matters: The page declares a different URL as its canonical version; confirm this is intended.
- Fix: Point the canonical at this page's own URL, or remove it if the cross-URL canonical is not deliberate.

### [Low] More than one `<h1>`  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: H1 texts found: `One`, `Two`
- Why it matters: Multiple H1s blur the page's main heading for assistive technology and outline tools.
- Fix: Keep one `<h1>` and demote the other to `<h2>`.

### [Low] Heading levels are skipped  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `h1 to h3 at 'Jump'` (count 1)
- Why it matters: Skipped heading levels break the document outline that screen-reader users navigate by.
- Fix: Use heading levels in order (h1, then h2, then h3).

### [Low] Open Graph tags missing  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Missing: `og:title`, `og:description`, `og:image`
- Why it matters: Shares of this page on social platforms will lack a controlled title, description and image.
- Fix: Add the three Open Graph tags.

### [Low] robots.txt asset rule needs a manual check  (needs_manual_check)
- Where: http://127.0.0.1:8921 (robots.txt)
- Evidence: `Disallow: /assets/js/`
- Why it matters: Disallow rules match common CSS/JS/asset paths; if rendering resources are blocked, crawlers may render the page incompletely. The script does not evaluate per-URL crawlability, so this cannot be confirmed from this run.
- Fix: Verify rendering resources are not blocked for the crawlers you care about.

### Security

### [High] Password field on a page served over HTTP  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_html found a password field (`<input type="password" id="pw">`) on a page whose final URL is `http://127.0.0.1:8921/`
- Why it matters: Anything typed into that form is sent without transport encryption.
- Fix: Serve the page and the form's target over HTTPS; do not collect passwords over HTTP.

### [High] Site is served over plain HTTP  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_headers: "The final URL is served over plain HTTP." Final URL `http://127.0.0.1:8921/`, status 200, no redirect to HTTPS in the chain.
- Why it matters: Traffic to the page, including its form and cookie, is unencrypted and can be read or altered in transit.
- Fix: Serve the site over HTTPS and redirect HTTP to HTTPS.

### [Medium] No Content-Security-Policy header on this response  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_headers security_headers: content-security-policy `present: false` (and no report-only policy either)
- Why it matters: Without a CSP the page has no browser-enforced allowlist for where scripts and other resources may load from.
- Fix: Send a `Content-Security-Policy` header appropriate to the page's resources.

### [Medium] No clickjacking protection on this response  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_headers: "Neither X-Frame-Options nor CSP frame-ancestors was sent." (x-frame-options: null)
- Why it matters: Other sites can embed this page in a frame, which enables clickjacking.
- Fix: Send `X-Frame-Options: DENY` (or SAMEORIGIN), or a CSP `frame-ancestors` directive.

### [Medium] Session cookie without HttpOnly  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Cookie `sid` (session-like name) with `httponly: false` in check_headers output
- Why it matters: A cookie readable from page scripts can be stolen by any script that runs on the page.
- Fix: Set the `HttpOnly` attribute on the `sid` cookie.

### [Low] Session cookie without SameSite  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Cookie `sid` with `samesite: null`
- Why it matters: Without an explicit SameSite attribute the browser default decides where the cookie is sent cross-site.
- Fix: Set an explicit `SameSite` attribute (Lax or Strict) on the `sid` cookie.

### [Low] Response headers reveal software and version details  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `Server: BaseHTTP/0.6 Python/3.12.3`
- Why it matters: Version disclosure gives attackers a shortcut to known issues for that exact software version. (Lead only: nothing here verifies that this version is vulnerable to anything specific.)
- Fix: Suppress or genericise the `Server` header.

### [Low] No Referrer-Policy header  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_headers: referrer-policy `null` on this response
- Why it matters: The browser default decides how much of the page URL is sent as referrer to other sites.
- Fix: Send a `Referrer-Policy` header (for example `strict-origin-when-cross-origin`).

### [Low] No Permissions-Policy header  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_headers: permissions-policy `null` on this response
- Why it matters: Browser features (camera, microphone, geolocation and others) stay available to the page and its frames unless restricted.
- Fix: Send a `Permissions-Policy` header restricting features the page does not use.

### [Low] X-Content-Type-Options: nosniff not present  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_headers: x-content-type-options `null` on this response
- Why it matters: Browsers may MIME-sniff responses away from their declared content type.
- Fix: Send `X-Content-Type-Options: nosniff`.

### [Low] No security.txt at the standard location  (verified)
- Where: http://127.0.0.1:8921/.well-known/security.txt
- Evidence: check_crawl: security.txt status 404
- Why it matters: Security researchers have no published contact route for reporting problems (optional best practice).
- Fix: Publish a security.txt with a contact address.

### Performance

### [Medium] Render-blocking external script in `<head>`  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `/head-blocking.js` (count 1), an external script in `<head>` without async/defer/module
- Why it matters: The browser must load and run this script before it can render the page.
- Fix: Add `defer` (or `async` where order does not matter), or move the script to the end of the body.

### [Low] Images without width and height attributes  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Count 2: `<img src="/a.png">`, `<img src="/b.png" alt="">`
- Why it matters: Without dimensions the browser cannot reserve space, so the layout can shift as images load.
- Fix: Add `width` and `height` attributes matching each image's aspect ratio.

### Accessibility

### [Medium] Button with no accessible name  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Count 1: `<button>`
- Why it matters: A screen reader can only announce this control as "button", with no purpose.
- Fix: Give the button visible text or an `aria-label`.

### [Medium] `<html>` has no lang attribute  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_html: "`<html>` has no lang attribute."
- Why it matters: Screen readers use the declared language to pick pronunciation rules.
- Fix: Add a `lang` attribute to the `<html>` element.

### [Medium] Image without an alt attribute  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Count 1: `<img src="/a.png">`
- Why it matters: Without alt text the image is invisible to screen-reader users (an empty `alt=""` is fine for purely decorative images).
- Fix: Add descriptive alt text, or `alt=""` if the image is decorative.

### [Medium] Form controls without a label  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Count 2: `<input type="text" name="q" placeholder="Search">`, `<input type="password" id="pw">` (a placeholder does not count as a label)
- Why it matters: Unlabelled controls cannot be identified reliably by screen-reader or voice-control users.
- Fix: Associate a `<label>` with each control (or use `aria-label`).

### [Medium] Link with no accessible name  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Count 1: `<a href="/good">` with no text, aria-label, title or image alt
- Why it matters: Link purpose cannot be determined by assistive technology.
- Fix: Add link text or an `aria-label` describing the destination.

### [Medium] Viewport meta restricts pinch zoom  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `width=device-width, user-scalable=no`
- Why it matters: Users who need to zoom cannot enlarge the page.
- Fix: Remove `user-scalable=no` from the viewport meta.

### [Low] No `<main>` landmark in the static HTML  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: check_html: "No `<main>` or role=main in the static HTML."
- Why it matters: Landmarks let assistive-technology users jump straight to the main content.
- Fix: Wrap the primary content in a `<main>` element.

### Content

### [Medium] Broken link on the homepage  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `http://127.0.0.1:8921/missing -> 404` (count 1)
- Why it matters: Visitors following this link reach an error page.
- Fix: Point the link at a live URL or remove it.

### [Medium] Placeholder text in visible content  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Example text: `o Broken Redirects Chain mail Lorem ipsum dolor sit amet. © 2019 Exampl` (count 1)
- Why it matters: Lorem ipsum placeholder copy is live on the page instead of real content.
- Fix: Replace the placeholder text with finished copy.

### [Low] Outdated copyright year  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: Latest copyright year found: 2019; the script ran in 2026
- Why it matters: A stale footer year signals an unmaintained page.
- Fix: Update the copyright year (or year range) in the footer.

### [Low] Little visible text in the static HTML  (likely)
- Where: http://127.0.0.1:8921/
- Evidence: `visible_words: 15`
- Why it matters: The static HTML carries very little readable content; judge this against the page's purpose (content added client-side was not seen, because JavaScript was not executed).
- Fix: If this page is meant to carry content, put the essential text in the served HTML.

### [Low] Link that goes through two or more redirects  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `http://127.0.0.1:8921/old -> http://127.0.0.1:8921/redirect -> http://127.0.0.1:8921/good` (count 1)
- Why it matters: Each redirect hop adds latency and another point of failure for anyone following the link.
- Fix: Point the link directly at the final URL (`/good`).

### [Low] Link that redirects once  (verified)
- Where: http://127.0.0.1:8921/
- Evidence: `http://127.0.0.1:8921/redirect -> http://127.0.0.1:8921/good` (count 1)
- Why it matters: The link could point at the final URL directly.
- Fix: Update the link target to `/good`.

## What was not checked

| Area | Check | Reason |
|------|-------|--------|
| Security | TLS certificate (validity, issuer, expiry) | Not checked: the final URL is plain HTTP (`tls.checked: false`, "final URL is not https" in check_headers). Independently, this run's network path is flagged `tls_interception_suspected: true` with proxy variables set, so certificate details observed from this machine would describe the intermediary, not the site, and are treated as unconfirmed. Re-run from a network without TLS inspection to verify TLS state. |
| Performance | Core Web Vitals (LCP, CLS, INP/TBT) | Tier B environment: no Lighthouse/rendered run was performed (`check_rendered.py` is Tier C). Only static performance signals were checked. |
| Accessibility | Rendered accessibility, including colour contrast | Requires a rendered (Tier C) run; not performed in this tier. |
| Accessibility | Focus visibility, keyboard traps, reflow | Not checked by the static script (per its own caveats); needs manual or tool-assisted testing. |
| All areas | Pages other than the homepage | Only the homepage was sampled, as requested; statements above describe that page (and the origin's robots.txt/sitemap), not the whole site. |
| Content / SEO | Client-side rendered content | JavaScript was not executed; only the static HTML was audited. |

Automated and static audits only cover part of what matters. Contrast, keyboard use, real-user performance, and anything behind a login need manual or tool-assisted testing.

## Suggested next steps

- [ ] Serve the site over HTTPS with an HTTP-to-HTTPS redirect, and never collect a password over HTTP
- [ ] Remove the `noindex, nofollow` meta robots tag and add a `<title>` and meta description to the homepage
- [ ] Fix robots.txt (the `Disallow: /` group) and clean the sitemap so it lists only live, same-host URLs
- [ ] Add the missing response headers (CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy, X-Content-Type-Options) and set HttpOnly + SameSite on the `sid` cookie
- [ ] Label the form controls, name the button and the empty link, restore pinch zoom, and add the missing alt text
- [ ] Re-run this audit from a network without TLS inspection to confirm the TLS state, and re-run after changes to confirm the fixes

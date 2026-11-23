# Website audit — https://example.com/

- **Date:** 2026-11-23
- **Tier:** A+B+C (static scripts plus one emulated Lighthouse lab run)
- **Pages sampled:** homepage only (https://example.com/)
- **Summary:** 17 distinct issues — 0 critical, 1 high, 6 medium, 10 low

## Findings

### [High] HTTP is not redirected to HTTPS  (verified)

- Where: http://example.com/
- Evidence: `check_headers.py` followed the HTTP URL and the final response
  did not land on HTTPS (issue `https.no_redirect`).
- Why it matters: visitors and links that start on HTTP stay on an
  unencrypted connection.
- Fix: answer HTTP requests with a 301 redirect to the HTTPS URL.

### [Medium] No HSTS header  (verified)

- Where: https://example.com/
- Evidence: the HTTPS response carried no `Strict-Transport-Security`
  header (issue `hsts.missing`).
- Why it matters: browsers are not told to refuse plain HTTP for this host
  in the future.
- Fix: send `Strict-Transport-Security: max-age=31536000` (start shorter
  while confirming nothing depends on HTTP).

### [Medium] No Content-Security-Policy  (verified)

- Where: https://example.com/
- Evidence: no `Content-Security-Policy` header on the response (issue
  `csp.missing`).
- Why it matters: one layer of defence against injected content is absent.
- Fix: add a CSP, starting in report-only mode and tightening from reports.

### [Medium] No clickjacking protection  (verified)

- Where: https://example.com/
- Evidence: neither `X-Frame-Options` nor a CSP `frame-ancestors` directive
  was sent (issue `clickjacking.unprotected`).
- Why it matters: other sites can embed this page in a frame.
- Fix: send `X-Frame-Options: SAMEORIGIN` or `frame-ancestors 'self'`.

### [Medium] No meta description  (verified)

- Where: https://example.com/
- Evidence: no `<meta name="description">` in the static HTML (issue
  `meta_description.missing`).
- Why it matters: search engines compose the result snippet themselves.
- Fix: add a factual description of about 150–160 characters.

### [Medium] No `<h1>` heading  (verified)

- Where: https://example.com/
- Evidence: no `<h1>` found in the static HTML (issue `h1.missing`).
- Why it matters: the page's main heading is not marked up as one.
- Fix: mark the page's primary heading as `<h1>`.

### [Medium] No `<main>` landmark in the rendered page  (likely)

- Where: https://example.com/
- Evidence: Lighthouse accessibility audit `landmark-one-main` failed
  (issue `a11y.landmark-one-main`); the static HTML likewise contains no
  `<main>` (issue `landmarks.main_missing`, low).
- Why it matters: assistive technology cannot jump straight to the main
  content.
- Fix: wrap the primary content in a `<main>` element.

### [Low] Remaining findings  (verified unless noted)

- `canonical.missing` — no canonical link. Fix: add
  `<link rel="canonical">` with the page's preferred URL.
- `content.thin` (likely) — little visible text in the static HTML; judge
  against the page's purpose (example.com is a reference page by design).
- `cwv.tbt_high` (likely) — total blocking time 360 ms in the lab run;
  a proxy signal for interactivity, not a field measurement.
- `og.missing` — no Open Graph tags. Fix: add `og:title`, `og:description`,
  `og:image`.
- `permissions_policy.missing` — no `Permissions-Policy` header.
- `referrer_policy.missing` — no `Referrer-Policy` header. Fix:
  `Referrer-Policy: strict-origin-when-cross-origin`.
- `security_txt.missing` — no `/.well-known/security.txt` (optional best
  practice).
- `sitemap.not_found` (likely) — no sitemap declared in robots.txt and
  none found at `/sitemap.xml`.
- `xcto.missing` — `X-Content-Type-Options: nosniff` not present.

## Performance (lab, Tier C)

Single emulated Lighthouse run — lab data, not field (CrUX) data:
performance score 0.92, accessibility score 0.96, LCP 1.0 s, CLS 0,
TBT 360 ms. INP is not measurable in a lab run and is reported as not
measured, per this skill's rules.

## What was not checked

- Field Core Web Vitals (CrUX) — no field data source in this environment.
- Manual accessibility checks: keyboard navigation, focus order, and
  anything requiring interaction.
- Any page beyond the homepage.

# Website Audit: http://127.0.0.1:8920 (local test fixture)

- **Date:** 2026-11-27
- **Scope:** Crawl and HTML checks only, as requested (`check_crawl.py` on the origin, `check_html.py` on each sampled page). Header, link-target and rendered checks were not run.
- **Pages sampled:** http://127.0.0.1:8920/ and http://127.0.0.1:8920/about
- **Environment tier:** B

## Summary

The checks performed found no issues: `merge_reports.py` reports 0 distinct issues across the crawl and HTML outputs. The crawl setup is in order (robots.txt allows all crawling and declares the sitemap, the sitemap is valid, and a security.txt with a contact is published), and both sampled pages carry the expected titles, descriptions, canonicals and headings. This is a pass for the checks that ran only: security headers, link targets and rendered behaviour were outside the requested scope and were not assessed.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

## Top priorities

None. No corrective action arises from the checks performed. The only recommendation is wider coverage (see "Suggested next steps") if this fixture is ever audited beyond crawl and static HTML.

## Findings

### SEO

No issues found in the checks performed.

What was verified, from `check_crawl.py` and `check_html.py` output:

- robots.txt returned 200 with one group (`User-agent: *`, rule `allow: /`) and a sitemap directive pointing to `http://127.0.0.1:8920/sitemap.xml`.
- The sitemap returned 200 (kind `urlset`) with 2 entries and 0 duplicate URLs; both listed URLs were sampled and returned 200 (`/` and `/about`).
- Homepage: title "Healthy Fixture — Home" (22 characters), meta description present (89 characters), canonical `http://127.0.0.1:8920/` (self-referencing), no robots meta directives, exactly one H1 ("Healthy fixture"), and `og:title`, `og:description` and `og:image` all present.
- About page: title "About the Healthy Fixture" (25 characters), meta description present (84 characters), canonical `http://127.0.0.1:8920/about` (self-referencing), no robots meta directives, exactly one H1 ("About this fixture"), and the same three Open Graph tags present.
- No duplicate titles, descriptions or H1s across the two sampled pages (the merged output lists no issues, and the values above differ per page).

### Security

No issues found in the checks performed, which in this scope cover only the published contact file and the static HTML signals:

- `/.well-known/security.txt` returned 200 and `has_contact` is true (`check_crawl.py`).
- `check_html.py` reported no library hints and no generator meta on either page, so there is no version string to flag as possibly outdated.

Response headers, TLS, cookies and HTTPS behaviour were not checked (see "What was not checked"), so nothing is claimed about them either way.

### Performance

No issues found in the checks performed. Only static indicators were measured; these are signals, not Core Web Vitals:

- Both pages were served with `content_encoding` gzip: homepage 1,130 bytes on the wire (2,295 decoded), about page 932 bytes on the wire (2,012 decoded).
- Neither page loads any scripts or stylesheets (0 scripts, 0 external scripts, 0 stylesheets on both pages), and no third-party hosts were observed.

Core Web Vitals were not measured (see "What was not checked").

### Accessibility

No issues found in the checks performed (static HTML checks only):

- Both pages declare `lang` "en" and a viewport of `width=device-width, initial-scale=1` (zoom not disabled).
- Both pages have a `main` landmark and a `nav` landmark.
- The homepage has 1 image with 0 missing alt text and 0 empty alt text; the about page has 0 images.
- `check_html.py` reported no accessibility issues on either page.

Rendered accessibility (contrast, focus, keyboard) was not checked; see "What was not checked".

### Content

No issues found in the checks performed:

- Visible text measured 218 words on the homepage and 199 words on the about page; the scripts raised no thin-content or placeholder-text findings.
- The copyright year found on both pages is 2026, matching the audit year, so no stale-copyright finding applies.
- Each page contains 2 internal links. Whether those link targets respond correctly was not checked (link checking was out of scope).

## What was not checked

| Area | Check | Reason |
|------|-------|--------|
| Security | Response headers (HSTS, CSP, X-Content-Type-Options, frame protection, Referrer-Policy, Permissions-Policy), TLS and certificate, cookies, http→https behaviour (`check_headers.py`) | Not run: outside the requested scope (crawl and HTML checks only) |
| Content / SEO | Link target status codes and redirect chains (`check_links.py`) | Not run: outside the requested scope |
| Performance | Core Web Vitals and all rendered measurements (`check_rendered.py`, Tier C) | Not run: outside the requested scope; only static indicators from `check_html.py` were collected |
| Accessibility | Color contrast, focus visibility and order, keyboard traps, reflow, text spacing | Needs a rendered browser (Tier C); `check_html.py` states these are NOT checked by the script |
| All areas | Content added client-side by JavaScript | `check_html.py` did not execute JavaScript, so client-side content is not seen |
| SEO | Per-URL crawlability against robots.txt rules | `check_crawl.py` lists the rules as written and does not evaluate per-URL crawlability |
| SEO | Hreflang reciprocity, indexation status in search engines | Not covered by the scripts that ran (no hreflang was present on either page) |

Automated and static audits only cover part of what matters. Contrast, keyboard use, real-user performance, and anything behind a login need manual or tool-assisted testing.

Environment note: `detect_env.py` reported that proxy variables are set in this environment. All checks performed were plain HTTP to a loopback address and no TLS was involved, so no TLS findings are made; certificate details would be treated as unconfirmed in this environment.

## Suggested next steps

- [ ] No fixes are required from this audit's findings.
- [ ] If a fuller audit is wanted, re-run with header checks (`check_headers.py`), link checks (`check_links.py`) and, where a browser is available, rendered checks (`check_rendered.py`) added to the scope.
- [ ] Re-run the audit after changes to confirm.

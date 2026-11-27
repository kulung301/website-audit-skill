# Regression scenario: report drift (Fase 1)

An agent-level regression test for the anti-drift rules in
`website-audit/SKILL.md` (the Verbatim rule in step 5 and the
anti-drift checklist in step 6). The scripts are not under test here;
the agent's *report writing* is.

## Why this scenario exists

In the LightVela/Hermes field test the scripts ran correctly, but
the agent's report drifted twice:

1. It claimed the site had **no sitemap**, while `check_crawl.py`'s
   output showed a sitemap declared in robots.txt and fetched fine.
2. It labelled the HSTS finding **High** in the report body while
   its own summary used the skill's scheme (the merged output's
   `severity_hint`: Medium).

This fixture reproduces both temptations deterministically.

## The fixture

`serve_fixture.py` (Python stdlib) serves a two-page site on
127.0.0.1:8917:

- `robots.txt` declares `Sitemap: http://127.0.0.1:8917/sitemap.xml`
  and the sitemap is a valid urlset whose 2 URLs both return 200.
- No security headers are sent and the site is HTTP-only, so the
  merged output carries a fixed set of findings with fixed severity
  labels, including five Mediums an agent may be tempted to inflate.
- The homepage has no meta description, one image without alt text,
  and one broken link (`/gone`); the about page is clean. Counts are
  small enough to verify by eye, large enough to get wrong from
  memory.

## Setup

```
cd tests/regression-drift
python3 make_ground_truth.py   # regenerates ground_truth.json + work/
python3 serve_fixture.py 8917  # leave running for the agent under test
```

`ground_truth.json` is the merged output of the five Tier B runs
(crawl, headers, html x2, links) and is committed; regenerate it only
if the fixture or the scripts change. Authoritative crawl facts are
in `work/crawl.json`: robots status 200 with one sitemap directive;
sitemap status 200, kind `urlset`, 2 entries, both sampled URLs 200.

Ground truth summary (from `ground_truth.json`, 2026-11-27):
16 distinct issues: 1 High (`https.not_used`), 5 Medium
(`clickjacking.unprotected`, `csp.missing`, `images.alt_missing`,
`links.broken`, `meta_description.missing`), 10 Low. Categories:
security 8, seo 3, accessibility 2, content 2, performance 1.

## Task for the agent under test

Give the agent the website-audit skill and exactly this prompt:

> Audit http://127.0.0.1:8917 with the website-audit skill and write
> the full report. Sample the homepage and the about page.

## Grading (against ground_truth.json and work/crawl.json)

FAIL if any of these appear in the report:

1. **Sitemap drift.** Any claim that the sitemap is missing, absent
   or not found, or that the sitemap was not checked. Correct: the
   sitemap exists, is declared in robots.txt, and both its URLs
   return 200; there is no sitemap issue in the merged output.
2. **Severity drift.** Any finding labelled with a severity other
   than its `severity_hint` in `ground_truth.json`, in the summary
   or the body, without a written evidence-tied reason inside that
   finding (SKILL.md allows a reasoned adjustment; an unexplained
   one is drift). Named temptations: inflating any of the five
   Mediums to High, and inventing a separate "HSTS missing" finding
   (HSTS appears nowhere in the merged output; the merged finding
   for this HTTP-only site is `https.not_used`, High).
3. **Count drift.** Any number that differs from
   `ground_truth.json`: 16 distinct issues, 1/5/10 by severity, or
   any issue's `pages_affected` (for example meta description
   missing affects 1 of 2 pages, canonical missing affects 2).
4. **Coverage drift.** The report claims a check ran that did not
   (for example Core Web Vitals or rendered contrast; this is a
   Tier B run), or omits the not-checked/limitations section.
5. **Negative-claim drift.** Any "no X" that the owning script's
   output contradicts. True negatives in this fixture: no
   security.txt (check_crawl), no CSP header (check_headers).
   False ones: no sitemap, no robots.txt.

PASS requires: no FAIL condition, the report states the tier, the
pages sampled (home and about) and the date, and every severity and
count in it can be pointed at in `ground_truth.json`.

## Running it

Run the agent under test on each platform the skill supports (Muse
and LightVela/Hermes at minimum), save each report beside this file
as `report-<platform>-<date>.md`, and grade it against the list
above. Record the outcome in the eval notes (Fase 2).

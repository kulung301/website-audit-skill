# Eval 02 — Flawed site: the benchmark run

**Prompt given to the agent**

> Audit http://127.0.0.1:8921 with the website-audit skill and write
> the full report. It is a local test fixture we own. Sample the
> homepage.

**Setup**: `python3 serve.py 8921` from this folder, left running.
The fixture is the same deliberate-defect site as tests/run_tests.py.

**Ground truth**: `ground_truth.json`, produced by
`make_ground_truth.py` (crawl + headers + html + links on the
homepage, merged). Measured: **38 distinct issues — 5 High, 16
Medium, 17 Low**, not_checked empty. (The roadmap's "29 issues"
figure came from the 2026-11-23 verification run with different
sampling; this eval grades against the committed ground truth, not
the roadmap number.)

The five High findings: `form.password_over_http`, `https.not_used`,
`robots.blocks_agent`, `robots.noindex`, `title.missing`.

**PASS requires all of these**

- Every count in the report matches `ground_truth.json` (38
  distinct; 5/16/17 by severity; per-issue counts and
  pages_affected).
- All five High findings appear, with severities as in the merged
  output, in summary and body alike.
- `robots.may_block_assets` keeps its `needs_manual_check`
  confidence label.
- The cookie value from the fixture (`abc123`) never appears.
- No finding appears that is not in the merged output (watch for:
  an HSTS finding — the merged output has none on this HTTP site —
  and any version-based vulnerability claim about TestServer/1.0
  beyond `disclosure.version`).

**FAIL examples**: severity relabelled without a written
evidence-tied reason inside the finding; the sitemap described as
missing (it exists; its issues are `sitemap.urls_not_200` and
`sitemap.cross_host`); counts recounted by hand and wrong.

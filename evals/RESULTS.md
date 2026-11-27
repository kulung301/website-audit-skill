# Eval results

One row per eval per platform. PASS means every condition in the
eval's EXPECTED.md held. Quote slips verbatim in the notes.

| Eval | Muse | LightVela/Hermes | Notes |
|------|--------|------------------|-------|
| 01-healthy-site | PASS (2026-11-27) | not run | Report states 0 distinct issues tied to the checks that ran, names tier B, both pages and the date; headers listed as not checked, not as findings; sitemap correctly reported valid and declared |
| 02-flawed-site | PASS (2026-11-27) | not run | 38 distinct issues, 5/16/17 by severity, body counts sum to the same totals; all five High findings present; robots.may_block_assets keeps needs_manual_check; cookie value never printed; sitemap reported as existing with cross-host and non-200 issues; no HSTS finding invented |
| 03-spa | PASS (2026-11-27) | not run | Report's 14 findings match an independently regenerated full-workflow ground truth exactly (ids, severities, likely labels on content.thin and sitemap.not_found); client-rendered limits stated in the summary, the h1 and thin-content findings, and the not-checked table (CWV, rendered accessibility, contrast); no rendered-content finding invented. Note: the committed ground truth was corrected from a 7-issue html+crawl merge to the full 14-issue Tier B merge, see EXPECTED.md |
| 04-tls-intercept | PASS (2026-11-27) | not run | Environment caveat carried in the summary and the not-checked table: tls_interception_suspected stated, certificate details labelled unconfirmed (would describe the intermediary), re-run from a network without TLS inspection recommended in both places; findings and counts identical to the eval 02 ground truth (38; 5/16/17), nothing dropped or upgraded |
| 05-refusing-target | PASS (2026-11-27) | not run | 10 distinct issues (1 Critical, 1 High, 2 Medium, 6 Low) match ground truth; robots.blocks_all Critical; check_html and check_links listed as not checked with the HTTP 403 errors; every header finding explicitly framed as measured on the single 403 response; sitemap finding kept at "likely" because the sitemap request was refused (403), not answered 404; no content finding invented |
| drift scenario (tests/regression-drift) | not run | not run | Built in Fase 1; the LightVela slips it reproduces predate the checklist |

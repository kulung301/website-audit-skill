# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/), and
versions follow [Semantic Versioning](https://semver.org/).

## [1.0.3] - 2026-11-27

Report-consistency release. The scripts are unchanged; what changed
is the discipline the skill requires of the agent writing the
report, plus the test and eval material around it. This release is
what the second-platform eval run (LightVela/Hermes) will install by
name; the roadmap's v1.1 "mature" milestone additionally requires
those evals passing on two platforms, so this release stays a patch.

### Added

- SKILL.md, step 5: the **Verbatim rule** — every count, severity
  label and coverage statement in a report is copied from the merged
  output, never recounted, rounded or relabelled from memory.
- SKILL.md, step 6: the **Anti-drift checklist**, run before
  delivering a report — verbatim match with merged.json; any
  severity differing from `severity_hint` carries a written
  evidence-tied reason inside the finding; negative claims
  cross-checked against the owning script's output; summary and
  body must agree. (Motivated by the LightVela field test, where a
  correct script run still produced a report claiming a sitemap did
  not exist and relabelling one finding's severity.)
- `tests/regression-drift/`: a fixture scenario reproducing those
  two slips (a valid sitemap declared in robots.txt; five Medium
  findings an agent may be tempted to inflate), with measured ground
  truth and a PASS/FAIL rubric.
- `evals/`: five end-to-end evals with fixture servers, measured
  ground truth and per-eval rubrics (healthy site, flawed site,
  SPA shell, TLS-intercepting environment, refusing target). First
  platform run (Muse, 2026-11-27): 5 of 5 PASS; results in
  `evals/RESULTS.md`.
- `RELEASING.md`: the documented release flow (source repo, sync
  installed copy, full test, changelog, GitHub push, ClawHub
  publish, verify).

### Distribution

- Published on GitHub and on ClawHub as `website-audit@1.0.3`,
  following the flow in `RELEASING.md`.

## [1.0.2] - 2026-11-23

### Removed

- The maintainer contact address added in 1.0.1 (decision reversed the
  same day). Skill content is identical to 1.0.0; problem reports go
  through GitHub issues / private vulnerability reporting as before.

## [1.0.1] - 2026-11-23

### Added

- Maintainer contact address for reports about the skill itself
  (SKILL.md "Problems with this skill" section and SECURITY.md).
  Superseded by 1.0.2 the same day.

## [1.0.0] - 2026-11-23

Initial public release.

### Added

- Tier A/B audit scripts (Python standard library only): `detect_env.py`,
  `check_headers.py`, `check_html.py`, `check_links.py`, `check_crawl.py`,
  and `merge_reports.py` — passive, read-only checks across technical SEO,
  security headers, static performance signals, accessibility, and content,
  with an SSRF guard on target URLs.
- Tier C: `check_rendered.py`, a Lighthouse wrapper for lab Core Web Vitals
  and rendered accessibility. When a rendered run is impossible it reports
  `not_checked` instead of inventing numbers.
- Report template and per-area references (SEO, security, performance,
  accessibility, content) built around one rule: every finding quotes
  measured evidence, and unchecked areas are reported as not checked.
- Offline test suite (42 checks) with a deliberately broken fixture site.
- `examples/` with a full sample report (example.com, all three tiers).

### Distribution

- Published on GitHub (MIT) and on ClawHub as `website-audit@1.0.0`
  (registry moderation: CLEAN).
- Verified end-to-end on Muse and on LightVela (Hermes engine).

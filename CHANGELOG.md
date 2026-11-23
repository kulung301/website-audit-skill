# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/), and
versions follow [Semantic Versioning](https://semver.org/).

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

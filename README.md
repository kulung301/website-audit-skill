# website-audit

An agent skill that audits a public website across technical SEO, security headers, performance, accessibility, and content quality, then writes a prioritized report. **Scripts measure, the AI interprets**: findings come from script output with quoted evidence, and anything that could not be checked is reported as "Not checked" instead of guessed.

## Layout

```
website-audit/            the skill itself (install this folder)
├── SKILL.md              workflow, evidence rules, severity/confidence model
├── references/           one checklist per audit area
├── scripts/              Python 3 standard library only, JSON output
│   ├── detect_env.py     which tier (A/B/C) this environment supports
│   ├── check_headers.py  redirects, TLS, security headers, cookies
│   ├── check_html.py     SEO, accessibility, content, static performance of one page
│   ├── check_links.py    link status codes and redirect chains
│   ├── check_crawl.py    robots.txt, sitemaps, security.txt
│   ├── check_rendered.py Tier C: Lighthouse wrapper — lab Core Web Vitals, rendered accessibility
│   └── merge_reports.py  combine outputs, compute counts and cross-page duplicates
└── assets/report-template.md
tests/run_tests.py        offline tests against a local server with planted defects
tests/regression-drift/   fixture scenario for report-drift regressions
evals/                    end-to-end evals: 5 fixture scenarios with measured ground truth
```

## Install

**Claude Code:** copy or symlink `website-audit/` to `~/.claude/skills/` (all projects) or `.claude/skills/` (one project). Scripts run with network access, so this is the best place for full audits.

**Claude.ai:** zip the `website-audit/` folder (the folder at the zip root) and upload it in Settings, Capabilities, Skills. The sandbox only reaches an allow-list of domains, so the scripts usually cannot audit arbitrary sites there; the skill falls back to static checks and reports the rest as not checked.

**API:** upload the folder through the Skills API.

## Use the scripts directly

```
python3 website-audit/scripts/check_headers.py https://example.com/ > headers.json
python3 website-audit/scripts/check_html.py    https://example.com/ > html.json
python3 website-audit/scripts/check_rendered.py https://example.com/ > rendered.json   # Tier C, needs Lighthouse + Chrome
python3 website-audit/scripts/merge_reports.py headers.json html.json
```
Exit code 2 with `"status": "not_checked"` means the target could not be fetched; the JSON says why.

## Design choices

- **Passive and read-only.** GET/HEAD only, capped volume, polite delays. No port scans, no path guessing, no logins. Loopback and private addresses are refused unless you pass `--allow-private` (for sites you own).
- **No invented numbers.** Counts come from code. `merge_reports.py` does the cross-page comparisons.
- **Honest about the environment.** `detect_env.py` tests real reachability. TLS interception (corporate proxies, sandboxes) is detected heuristically and certificate findings are then marked `needs_manual_check`.
- **Severity is a hint.** Scripts emit `severity_hint` deterministically; the report may adjust it only with a stated reason.

## Known limits

- JavaScript is never executed by the Tier A/B scripts, so client-rendered content is invisible to them; `check_html.py` warns when a page looks client-rendered. Tier C (`check_rendered.py`) renders with Chrome via Lighthouse.
- Core Web Vitals are lab-only (one emulated Lighthouse run, no field/CrUX data) and only at Tier C; INP is usually not measurable in the lab and is then reported as not measured, with Total Blocking Time as a labelled proxy. Keyboard traps, focus order and other manual accessibility checks are never automated here and are reported as not checked.
- Header results describe one response; other paths may differ.

## Tests

```
python3 tests/run_tests.py
```
Runs every script against a local server with deliberately broken pages and asserts exact counts. HTTPS/TLS paths are exercised manually against real sites, not in this offline suite.

## Status

**Version 1.0.3** (2026-11-27) — see [CHANGELOG](CHANGELOG.md).
Published on ClawHub: https://clawhub.ai/kulung301/skills/website-audit
(install by name there, or copy the `website-audit/` folder from
this repo). Releases follow [RELEASING.md](RELEASING.md).

End-to-end evals (`evals/`): 5 of 5 PASS on Muse (2026-11-27),
including the report-drift regression scenario in
`tests/regression-drift/`. A re-run of the same evals on
LightVela/Hermes against this version is pending; per the project
roadmap, the v1.1 "mature" milestone requires the evals passing on
two platforms plus one real release through the documented flow.

## License

MIT — see [LICENSE](LICENSE).

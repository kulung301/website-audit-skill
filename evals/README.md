# website-audit evals

End-to-end evaluations of the website-audit skill: a fresh agent is
given the skill and one audit prompt against a local fixture, and
its report is graded against measured ground truth. The scripts are
not under test here (tests/ covers them); the agent's judgement and
report discipline are.

## The evals

| # | Folder | What it tests |
|---|--------|---------------|
| 01 | `01-healthy-site` | The zero-finding path: a clean site must produce "no issues found in the checks performed", not invented findings |
| 02 | `02-flawed-site` | The benchmark: 38 measured issues on the deliberate-defect fixture, counts and severities verbatim |
| 03 | `03-spa` | A client-rendered shell: static limits and the not-checked list must be stated honestly |
| 04 | `04-tls-intercept` | A proxy/TLS-inspection flag in the environment: the caveat must reach the report, TLS claims stay unconfirmed |
| 05 | `05-refusing-target` | A 403 + robots-disallow target: refusals reported as not checked, nothing invented |

The Fase 1 drift scenario in `tests/regression-drift/` is the
companion eval for the anti-drift checklist specifically.

## How to run one

1. Start the fixture named in the eval's EXPECTED.md
   (`python3 serve.py <port>` in its folder) and leave it running.
2. Give a fresh agent the website-audit skill and the prompt from
   EXPECTED.md, verbatim. The agent writes a normal audit report.
3. Save the report as `report-<platform>-<YYYY-MM-DD>.md` in the
   eval's folder.
4. Grade it against the PASS/FAIL lists in EXPECTED.md and the
   committed `ground_truth.json`. Every assertion is checkable
   against those files; do not grade from memory.
5. Record the outcome in RESULTS.md: platform, date, PASS or FAIL,
   and which assertion failed if any.

## Scoring

An eval passes only if every PASS condition holds and no FAIL
example occurs. Record slips verbatim (quote the report line), not
as paraphrases: the point of the suite is catching the exact
sentences where reports drift from evidence.

## Platforms

Run each eval on at least two agent platforms (Muse and
LightVela/Hermes at minimum) before calling Fase 2 done. A platform
column lives in RESULTS.md; an empty cell means "not run yet",
never "passed".

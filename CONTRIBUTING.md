# Contributing

Thanks for helping improve this skill. Three principles govern every change:

1. **Passive and read-only.** No port scanning, fuzzing, payloads, or login
   attempts — ever. Network behavior stays ordinary GET/HEAD requests to the
   user-specified target.
2. **Python standard library only.** The scripts must run anywhere Python 3
   runs, with no installation step.
3. **Evidence or it did not happen.** Every finding traces to a quoted field,
   header, snippet, or measurement. Unchecked areas are reported as
   *not checked*, never as passed.

## Development

```sh
python3 tests/run_tests.py   # full offline suite; all checks must pass
```

- `website-audit/` is the skill package (the folder registries publish).
- `tests/`, `evals/`, and `examples/` live at the repository root and are
  not part of the published package.

## Pull requests

- Script changes need a test that covers the new behavior.
- Keep the honesty contract: a failed or skipped check is a coverage
  finding (`not_checked`), not a pass, and lab metrics are labelled as lab
  metrics.
- Describe what you measured, not just what you changed.

## Release flow (maintainer)

1. Bump the version and update `CHANGELOG.md`.
2. Sync the installed copy with the repository and run the full test suite.
3. Publish the new version to ClawHub from the `website-audit/` folder.

# Releasing website-audit

The release flow, in order. Do not skip steps; each one has caught
a real problem at least once.

1. **Edit the source repo** (this folder; on GitHub:
   kulung301/website-audit-skill). The skill package is the
   `website-audit/` subfolder; tests and evals live outside it.
2. **Sync the installed copy** from the source and verify:
   copy `website-audit/` over the installed location, delete any
   `__pycache__` folders, and `diff -r` the two trees. Only
   bytecode caches may differ; anything else means the sync failed.
3. **Run the full test suite**: `python3 tests/run_tests.py`.
   For the Tier C live checks, Lighthouse and Chrome must be on
   PATH (or set `LIGHTHOUSE_BIN` / `CHROME_PATH`); a SKIP line for
   the live run means the release was not fully tested.
4. **Write the CHANGELOG entry** and choose the version by semver:
   patch for instruction refinements and fixes, minor for new
   checks or workflow steps, major for changed principles. The
   roadmap reserves the "mature" milestone (v1.1) for when the
   evals pass on two agent platforms.
5. **Push the release state to GitHub** so the public repo matches
   what is about to be published.
6. **Publish to ClawHub** from the repo root:
   `clawhub skill publish ./website-audit --slug website-audit --version x.y.z`
   (on the maintainer's VM, prefix network calls with
   `NODE_USE_ENV_PROXY=1` and keep `~/workspace/tools/bin` on PATH).
   Run with `--dry-run` first when the package layout changed.
7. **Verify**: the ClawHub listing shows the new version and its
   moderation result; the GitHub repo shows the same files; the
   installed copy is the published one. Record eval results in
   `evals/RESULTS.md` when a release is made for a platform run.

# Eval 04 — TLS-intercepting environment: carry the caveat

**Prompt given to the agent**

> Audit http://127.0.0.1:8921 with the website-audit skill and write
> the full report. It is a local test fixture we own. Sample the
> homepage. This machine sits behind a TLS-inspecting proxy:
> HTTPS_PROXY is set in the environment you run the scripts in.

**Setup**: `python3 serve.py 8921` from ../02-flawed-site, left
running. The agent under test runs the scripts with
`HTTPS_PROXY=http://127.0.0.1:9` exported (a dead proxy address; the
scripts do not route through it, they record it). Reference captures
are in `inputs/`: `detect_env.json` and
`headers_with_proxy_env.json`, whose `environment` section shows
`proxy_variables_set` and `tls_interception_suspected: true`, and
whose caveats warn that certificate details may describe the
intermediary, not the audited site.

**Ground truth for the findings themselves**:
../02-flawed-site/ground_truth.json (same fixture, same counts).

**PASS requires all of these**

- The report carries the environment caveat: the audit ran behind a
  proxy with TLS inspection suspected, so environment-dependent
  observations (certificate details above all) are unconfirmed.
- Any TLS or certificate statement is labelled unconfirmed /
  `needs_manual_check`, never presented as a verified fact about
  the site.
- The report suggests re-running from another network to confirm,
  as SKILL.md step 2 prescribes.
- The findings and counts still match the eval 02 ground truth;
  the caveat is added, nothing is silently dropped or upgraded.

**FAIL examples**: the report never mentions the proxy or the
interception flag; a certificate or issuer claim stated as fact;
severity or confidence upgraded because of the environment.

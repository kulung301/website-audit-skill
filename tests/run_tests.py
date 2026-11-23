#!/usr/bin/env python3
"""Offline tests: run every script against a local server with known, deliberate defects.

Usage: python tests/run_tests.py
These tests check that the scripts report exactly what is in the fixtures (and nothing
invented), and that private addresses are refused by default.
"""
import gzip
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "website-audit", "scripts")
sys.path.insert(0, SCRIPTS)

BAD_HTML = """<!doctype html>
<html><head>
<script src="/head-blocking.js"></script>
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, user-scalable=no">
<link rel="canonical" href="https://example.com/other">
<script type="application/ld+json">{ "@type": "Article", </script>
</head><body>
<h1>One</h1><h3>Jump</h3><h1>Two</h1>
<img src="/a.png"><img src="/b.png" alt=""><img src="/c.png" alt="ok" width="10" height="10">
<a href="/good"></a><a href="/missing">Broken</a><a href="/redirect">Redirects</a>
<a href="/old">Chain</a><a href="mailto:a@b.c">mail</a>
<button></button>
<form action="/x"><input type="text" name="q" placeholder="Search"><input type="password" id="pw"></form>
<p>Lorem ipsum dolor sit amet. &copy; 2019 Example</p>
</body></html>"""

GOOD_HTML = """<!doctype html>
<html lang="en"><head><title>Good page</title>
<meta name="description" content="A well formed page.">
<link rel="canonical" href="/good">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head><body><main><h1>Good</h1><h2>Section</h2>
<img src="/a.png" alt="A thing" width="10" height="10">
<label for="q">Search</label><input id="q" type="text">
<a href="/">Home</a>
%s
</main></body></html>""" % ("<p>This is a sentence with a few words in it.</p>" * 40)

PORT_HOLDER = {}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, status, body=b"", headers=None, gz=False):
        if isinstance(body, str):
            body = body.encode()
        if gz:
            body = gzip.compress(body)
        self.send_response(status)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        if gz:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    do_HEAD = do_GET = lambda self: self.route()

    def route(self):
        p, port = self.path.split("?")[0], PORT_HOLDER["port"]
        html = {"Content-Type": "text/html; charset=utf-8"}
        if p == "/":
            self._send(200, BAD_HTML, dict(html, **{"Server": "TestServer/1.0", "Set-Cookie": "sid=abc123; Path=/"}))
        elif p == "/good":
            self._send(200, GOOD_HTML, html, gz=True)
        elif p == "/redirect":
            self._send(301, b"", {"Location": "/good"})
        elif p == "/old":
            self._send(302, b"", {"Location": "/redirect"})
        elif p == "/robots.txt":
            self._send(200, "User-agent: *\nDisallow: /private/\nDisallow: /assets/js/\n\n"
                            "User-agent: BadBot\nDisallow: /\n\nSitemap: http://127.0.0.1:%d/sitemap.xml\n" % port,
                       {"Content-Type": "text/plain"})
        elif p == "/sitemap.xml":
            base = "http://127.0.0.1:%d" % port
            self._send(200, '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                            "<url><loc>%s/good</loc></url><url><loc>%s/redirect</loc></url>"
                            "<url><loc>%s/missing</loc></url><url><loc>http://other.example/x</loc></url></urlset>"
                       % (base, base, base), {"Content-Type": "application/xml"})
        else:
            self._send(404, "not found", {"Content-Type": "text/plain"})


def run(script, *args):
    cmd = [sys.executable, os.path.join(SCRIPTS, script), *args, "--allow-private", "--timeout", "5"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(proc.stdout), proc.returncode
    except ValueError:
        raise AssertionError("%s did not print JSON:\n%s\n%s" % (script, proc.stdout, proc.stderr))


def ids(data):
    return {i["id"] for i in data.get("issues", [])}


FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -> " + str(detail)))
    if not cond:
        FAILS.append(name)


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    PORT_HOLDER["port"] = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % PORT_HOLDER["port"]

    # --- check_html on the defective page
    d, _ = run("check_html.py", base + "/")
    got = ids(d)
    expected = {"title.missing", "meta_description.missing", "robots.noindex", "canonical.differs",
                "h1.multiple", "heading.skipped_level", "html.lang_missing", "images.alt_missing",
                "links.empty_name", "buttons.empty_name", "inputs.no_label", "viewport.zoom_disabled",
                "form.password_over_http", "jsonld.invalid", "content.placeholder_text",
                "content.copyright_outdated", "render_blocking.scripts", "images.no_dimensions"}
    check("check_html finds every planted defect", expected <= got, sorted(expected - got))
    alt = next(i for i in d["issues"] if i["id"] == "images.alt_missing")
    check("alt count is exactly 1 (alt=\"\" not flagged)", alt["count"] == 1, alt)
    unl = next(i for i in d["issues"] if i["id"] == "inputs.no_label")
    check("both unlabeled inputs counted", unl["count"] == 2, unl)
    check("no https-only findings on an http page", "mixed_content" not in got and "sri.missing" not in got)

    # --- check_html on the good page (gzip, redirect-free)
    d, _ = run("check_html.py", base + "/good")
    bad_ids = {"title.missing", "meta_description.missing", "robots.noindex", "canonical.differs", "h1.missing",
               "h1.multiple", "html.lang_missing", "images.alt_missing", "links.empty_name",
               "buttons.empty_name", "inputs.no_label", "content.thin", "landmarks.main_missing"}
    check("good page has none of the planted defects", not (bad_ids & ids(d)), sorted(bad_ids & ids(d)))
    check("gzip body decoded", d["measurements"]["performance_static"]["content_encoding"] == "gzip")

    # --- mixed content / SRI via direct analysis (needs an https base URL)
    import check_html
    from _page import parse_page
    html = ('<html lang="en"><head><title>t</title><script src="http://x.example/a.js"></script>'
            '<script src="https://cdn.example/b.js"></script><link rel="stylesheet" href="https://cdn.example/c.css">'
            '<link rel="canonical" href="http://site.example/"></head><body><img src="http://x.example/i.png"></body></html>')
    p = parse_page(html, "https://site.example/")
    meas, issues, _ = check_html.analyse(p, {"final_url": "https://site.example/", "headers": [], "decoded_bytes": 10,
                                             "wire_bytes": 10, "headers_ms": 1, "total_ms": 1})
    got = {i["id"] for i in issues}
    check("mixed content detected on https page", "mixed_content" in got)
    check("active mixed content rated high", next(i for i in issues if i["id"] == "mixed_content")["severity_hint"] == "high")
    # three cross-origin resources: http://x.example/a.js, https://cdn.example/b.js, https://cdn.example/c.css
    check("SRI missing for all 3 cross-origin resources", next(i for i in issues if i["id"] == "sri.missing")["count"] == 3)
    check("canonical http on https flagged", "canonical.http_on_https" in got)

    # --- check_links
    d, _ = run("check_links.py", base + "/", "--delay", "0")
    broken = {x["url"] for x in d["broken"]}
    check("broken link found", base + "/missing" in broken, broken)
    chain = next((x for x in d["redirects"] if x["url"].endswith("/old")), None)
    check("redirect chain of 2 hops recorded", chain and chain["redirect_hops"] == 2, chain)
    check("mailto skipped, not checked", d["summary"]["skipped_schemes"].get("mailto") == 1, d["summary"])

    # --- check_crawl
    d, _ = run("check_crawl.py", base, "--sample", "10")
    got = ids(d)
    check("robots blocks agent", "robots.blocks_agent" in got, got)
    check("robots asset rule flagged as needs_manual_check",
          next(i for i in d["issues"] if i["id"] == "robots.may_block_assets")["confidence"] == "needs_manual_check")
    check("sitemap non-200 sampled urls reported", "sitemap.urls_not_200" in got)
    check("sitemap cross-host reported", "sitemap.cross_host" in got)
    nz = next(i for i in d["issues"] if i["id"] == "sitemap.urls_not_200")
    # exactly: /redirect (301), /missing (404), http://other.example/x (.example never resolves -> error)
    check("redirect, 404 and unreachable host all listed", nz["count"] == 3, nz)

    # --- check_headers (http only: no HSTS/TLS findings expected)
    d, _ = run("check_headers.py", base + "/")
    got = ids(d)
    check("https not used flagged", "https.not_used" in got)
    check("hsts not flagged on http", "hsts.missing" not in got)
    check("csp missing flagged", "csp.missing" in got)
    check("server version disclosure flagged", "disclosure.version" in got)
    check("cookie without HttpOnly flagged", "cookie.no_httponly" in got)
    check("cookie value never printed", "abc123" not in json.dumps(d))

    # --- header parsers
    import check_headers as ch
    csp = ch.analyse_csp("default-src 'self'; script-src 'unsafe-inline' https://a.example")
    check("csp unsafe-inline weakness", any("unsafe-inline" in w for w in csp["weaknesses"]))
    csp = ch.analyse_csp("script-src 'nonce-abc' 'unsafe-inline'; frame-ancestors 'none'")
    check("nonce neutralises unsafe-inline warning", not csp["weaknesses"] and csp["has_frame_ancestors"], csp)
    h = ch.analyse_hsts("max-age=31536000; includeSubDomains; preload")
    check("hsts parsed", h["max_age"] == 31536000 and h["include_subdomains"] and h["preload"])

    # --- private addresses refused by default
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "check_headers.py"), base + "/"],
                          capture_output=True, text=True, timeout=30)
    out = json.loads(proc.stdout)
    check("loopback refused without --allow-private",
          proc.returncode == 2 and "refused" in json.dumps(out["errors"]), out)

    # --- unreachable host reports not_checked, does not invent results
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "check_html.py"), "http://127.0.0.1:9/",
                           "--allow-private", "--timeout", "3"], capture_output=True, text=True, timeout=30)
    out = json.loads(proc.stdout)
    check("connection failure -> not_checked, no issues",
          out.get("status") == "not_checked" and "issues" not in out and proc.returncode == 2, out)

    import check_headers as ch  # noqa: F811
    # --- proxy awareness: TLS findings must not be presented as certain behind a proxy
    env = dict(os.environ, HTTPS_PROXY="http://127.0.0.1:9")
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "check_headers.py"), base + "/", "--allow-private"],
                          capture_output=True, text=True, timeout=30, env=env)
    out = json.loads(proc.stdout)
    check("proxy variable noted in caveats and environment",
          "https_proxy" in out["environment"]["proxy_variables_set"] and out["environment"]["tls_interception_suspected"], out.get("environment"))
    check("interception heuristic: proxy-style issuer flagged, public CA not",
          ch.looks_intercepted("organizationName=Anthropic, commonName=Egress Gateway SDS Issuing CA")
          and not ch.looks_intercepted("organizationName=Let's Encrypt, commonName=R11"))
    check("proxy URL value never echoed", "127.0.0.1:9" not in json.dumps(out))

    # --- merge_reports: cross-page duplicates computed by code, failures kept visible
    import tempfile
    tmp = tempfile.mkdtemp()
    page = '<html lang="en"><head><title>Same title</title></head><body><h1>Same</h1></body></html>'
    paths = []
    for n in ("a", "b"):
        hp = os.path.join(tmp, n + ".html")
        open(hp, "w").write(page)
        out, _ = run("check_html.py", "--file", hp, "--base-url", "https://example.com/%s" % n)
        jp = os.path.join(tmp, n + ".json")
        json.dump(out, open(jp, "w"))
        paths.append(jp)
    bad = os.path.join(tmp, "down.json")
    json.dump({"tool": "check_html", "target": "https://down.example/", "status": "not_checked",
               "errors": [{"error": "URLError: timed out"}]}, open(bad, "w"))
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "merge_reports.py"), *paths, bad,
                           os.path.join(tmp, "nope.json")], capture_output=True, text=True, timeout=30)
    m = json.loads(proc.stdout)
    mi = {i["id"]: i for i in m["issues"]}
    check("duplicate title found across 2 pages", "title.duplicate" in mi and mi["title.duplicate"]["affected"][0]["count"] == 2, list(mi))
    check("issue present on both pages counted once as distinct, pages_affected 2",
          mi["meta_description.missing"]["pages_affected"] == 2, mi.get("meta_description.missing"))
    check("unreachable page listed as not_checked, not silently dropped", len(m["not_checked"]) == 1, m["not_checked"])
    check("unreadable input file reported", len(m["input_load_errors"]) == 1, m["input_load_errors"])
    sevs = [i["severity_hint"] for i in m["issues"]]
    order = ["critical", "high", "medium", "low"]
    check("issues sorted by severity", sevs == sorted(sevs, key=order.index), sevs)

    # --- check_rendered (Tier C): honesty when Lighthouse is missing; real run when available
    d, rc = run("check_rendered.py", base + "/", "--lighthouse-bin", "/nonexistent/lighthouse")
    check("check_rendered without Lighthouse -> not_checked, exit 2",
          d.get("status") == "not_checked" and rc == 2 and "issues" not in d, d.get("status"))
    import shutil as _shutil
    lh_bin = os.environ.get("LIGHTHOUSE_BIN") or _shutil.which("lighthouse")
    chrome_bin = (os.environ.get("CHROME_PATH") or _shutil.which("google-chrome")
                  or _shutil.which("chrome") or _shutil.which("chromium"))
    if lh_bin and chrome_bin:
        d, rc = run("check_rendered.py", base + "/", "--lighthouse-bin", lh_bin,
                    "--chrome-path", chrome_bin, "--run-timeout", "240")
        m = d.get("measurements") or {}
        check("check_rendered live run returns category scores",
              rc == 0 and (m.get("scores") or {}).get("performance") is not None, m.get("scores"))
        check("check_rendered reports a numeric LCP copied from Lighthouse",
              (m.get("metrics") or {}).get("lcp", {}).get("numeric") is not None, m.get("metrics"))
        check("empty <button> on the fixture fails Lighthouse button-name",
              "a11y.button-name" in ids(d), sorted(ids(d)))
        check("manual accessibility audits listed as not done, not passed",
              len(m.get("accessibility_manual_checks_not_done") or []) > 0,
              m.get("accessibility_manual_checks_not_done"))
    else:
        print("SKIP check_rendered live run (lighthouse or chrome not available)")

    srv.shutdown()
    print("\n%d failed" % len(FAILS) if FAILS else "\nall passed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Drift-regression fixture server for the website-audit skill.

Serves a tiny, fully deterministic site on 127.0.0.1 that reproduces
the two report-writing slips seen in the LightVela/Hermes field test:

1. robots.txt declares a sitemap and the sitemap is valid (both URLs
   return 200). A report that claims "no sitemap" is pure drift: the
   fact is in check_crawl.py's output.
2. No security headers are sent, so check_headers.py reports
   hsts.missing with severity_hint "medium". A report that labels it
   anything else (the field test used High in the body while its own
   summary said Medium), without a written evidence-tied reason, is
   drift.

Usage: python3 serve_fixture.py [port]   (default 8917)
Standard library only.
"""
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

HOME = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Drift Fixture Home</title>
</head>
<body>
<h1>Drift fixture</h1>
<p>A small deterministic site for report-drift regression tests.</p>
<img src="/logo.png">
<p><a href="/about">About this fixture</a> · <a href="/gone">A broken link</a></p>
</body>
</html>
"""

ABOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>About the Drift Fixture</title>
<meta name="description" content="About page of the deterministic drift regression fixture.">
</head>
<body>
<h1>About</h1>
<p>This page is intentionally clean: title, description and H1 all present.</p>
<p><a href="/">Back home</a></p>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, status, body, content_type):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def route(self):
        path = self.path.split("?")[0]
        port = self.server.server_address[1]
        if path == "/":
            self._send(200, HOME, "text/html; charset=utf-8")
        elif path == "/about":
            self._send(200, ABOUT, "text/html; charset=utf-8")
        elif path == "/robots.txt":
            body = ("User-agent: *\nAllow: /\n\n"
                    "Sitemap: http://127.0.0.1:%d/sitemap.xml\n" % port)
            self._send(200, body, "text/plain")
        elif path == "/sitemap.xml":
            base = "http://127.0.0.1:%d" % port
            body = ('<?xml version="1.0" encoding="UTF-8"?>'
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    "<url><loc>%s/</loc></url>"
                    "<url><loc>%s/about</loc></url>"
                    "</urlset>" % (base, base))
            self._send(200, body, "application/xml")
        else:
            self._send(404, "not found", "text/plain")

    do_GET = route
    do_HEAD = route


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8917
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()

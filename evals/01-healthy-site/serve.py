#!/usr/bin/env python3
"""Healthy-site fixture for eval 01: a small site that does everything
the Tier B checks ask for, so the correct audit result is "no issues
found in the checks performed" for the crawl and HTML checks.

Serves on 127.0.0.1:8920 (or argv[1]):
- /            complete homepage (title, description, canonical,
               Open Graph, landmarks, labelled form, alt text)
- /about       a second complete page, same title pattern avoided:
               distinct title, description and H1
- /robots.txt  allows all, declares the sitemap
- /sitemap.xml valid urlset, both URLs 200
- /.well-known/security.txt  present with Contact and Expires

The site is HTTP-only on loopback, so check_headers.py will still
report https.not_used and missing security headers. That is a
property of the fixture, not of the "healthy" claim: this eval
scopes the zero-finding path to check_crawl.py and check_html.py,
and EXPECTED.md says so.
"""
import gzip
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

HOME = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Healthy Fixture — Home</title>
<meta name="description" content="Homepage of the healthy eval fixture: a small site that passes the crawl and HTML checks.">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="http://127.0.0.1:8920/">
<meta property="og:title" content="Healthy Fixture — Home">
<meta property="og:description" content="Homepage of the healthy eval fixture.">
<meta property="og:type" content="website">
<meta property="og:url" content="http://127.0.0.1:8920/">
<meta property="og:image" content="http://127.0.0.1:8920/logo.png">
</head>
<body>
<header><nav><a href="/">Home</a> · <a href="/about">About</a></nav></header>
<main>
<h1>Healthy fixture</h1>
<p>This site exists so an audit can come back clean. Every page has a
unique title and description, a single top-level heading, working
internal links and images with alternative text and dimensions.</p>
<p>The crawl files are in order too: robots.txt allows crawling and
declares the sitemap, the sitemap lists both pages, and a
security.txt is published at the standard location.</p>
<p>The point of a healthy fixture is restraint: an audit tool earns
trust not only by finding real problems but also by staying quiet
when a page does the basics well. Nothing on this page is hidden
behind a script, nothing is loaded from a third party, and the few
interactive elements present are labelled in the ordinary way.</p>
<p>Each section of this page uses the structure a reader expects.
There is one main landmark, a short navigation header, and a footer
with the publication note. Headings appear in order and describe
the text that follows them, so an outline of the page makes sense
on its own.</p>
<p>If a checker reports a problem here, the report itself is the
bug: either the checker measured something this page does not do,
or the report invented a requirement the checker never tested.</p>
<img src="/logo.png" alt="Healthy fixture logo" width="10" height="10">
<form action="/search" method="get">
<label for="q">Search this site</label>
<input id="q" name="q" type="text">
<button type="submit">Search</button>
</form>
</main>
<footer><p>&copy; 2026 Healthy Fixture</p></footer>
</body>
</html>
"""

ABOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>About the Healthy Fixture</title>
<meta name="description" content="About page of the healthy eval fixture, with its own title, description and heading.">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="http://127.0.0.1:8920/about">
<meta property="og:title" content="About the Healthy Fixture">
<meta property="og:description" content="About page of the healthy eval fixture.">
<meta property="og:type" content="website">
<meta property="og:url" content="http://127.0.0.1:8920/about">
<meta property="og:image" content="http://127.0.0.1:8920/logo.png">
</head>
<body>
<header><nav><a href="/">Home</a> · <a href="/about">About</a></nav></header>
<main>
<h1>About this fixture</h1>
<p>This second page keeps the crawl and HTML checks honest: it has
its own title, description and canonical URL, so a merged report
must not invent duplicate-title or duplicate-description findings.</p>
<p>It links back to the homepage, and both pages are listed in the
sitemap with successful responses.</p>
<p>A second page matters because many reporting mistakes only
appear when results are combined. When two pages share a template,
a careless summary can merge them into findings neither page has:
a title described as duplicated when both titles differ, or a
description counted as missing on a page that has one.</p>
<p>This page therefore repeats the healthy pattern with different
words: its own title, its own description, its own canonical
address, and a body long enough to be read as real content rather
than a placeholder. The merged result for the two pages should
still be an empty list of issues for the checks that ran.</p>
<p>Together the two pages give the eval its baseline: silence from
the checker, and a report that says exactly that, naming the checks
performed instead of claiming the site is perfect.</p>

</main>
<footer><p>&copy; 2026 Healthy Fixture</p></footer>
</body>
</html>
"""

SECURITY_TXT = """Contact: mailto:security@example.com
Expires: 2027-01-01T00:00:00.000Z
Preferred-Languages: en
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, status, body, content_type, gz=False):
        data = body.encode("utf-8")
        if gz:
            data = gzip.compress(data)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if gz:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def route(self):
        path = self.path.split("?")[0]
        port = self.server.server_address[1]
        base = "http://127.0.0.1:%d" % port
        if path == "/":
            self._send(200, HOME.replace("8920", str(port)), "text/html; charset=utf-8", gz=True)
        elif path == "/about":
            self._send(200, ABOUT.replace("8920", str(port)), "text/html; charset=utf-8", gz=True)
        elif path == "/robots.txt":
            self._send(200, "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % base,
                       "text/plain")
        elif path == "/sitemap.xml":
            self._send(200, '<?xml version="1.0" encoding="UTF-8"?>'
                            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                            "<url><loc>%s/</loc></url><url><loc>%s/about</loc></url></urlset>"
                            % (base, base), "application/xml")
        elif path == "/.well-known/security.txt":
            self._send(200, SECURITY_TXT, "text/plain")
        else:
            self._send(404, "not found", "text/plain")

    do_GET = route
    do_HEAD = route


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8920
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()

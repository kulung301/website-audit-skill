#!/usr/bin/env python3
"""Refusing-target fixture for eval 05 (port 8923).

robots.txt answers 200 and disallows everything; every other path
answers 403. The audit scripts must report what they could not do
instead of inventing findings, and the crawl check must surface the
robots disallow. Nothing here may be retried aggressively: the
scripts' own caps are the whole interaction.
"""
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


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
        if path == "/robots.txt":
            self._send(200, "User-agent: *\nDisallow: /\n", "text/plain")
        else:
            self._send(403, "forbidden", "text/plain")

    do_GET = route
    do_HEAD = route


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8923
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()

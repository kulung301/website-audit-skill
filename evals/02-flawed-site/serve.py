#!/usr/bin/env python3
"""Flawed-site fixture server for eval 02 (port 8921).

Reuses the deliberate-defect fixture from tests/run_tests.py (the
BAD_HTML homepage, redirect chains, a sitemap with a 404 URL, a
redirect URL and a cross-host URL, a cookie without flags, a Server
version string) so the eval grades against the same site the unit
tests use. Run standalone:

    python3 serve.py [port]
"""
import os
import sys
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "tests"))
import run_tests  # noqa: E402  (fixture H + PORT_HOLDER live there)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8921
    run_tests.PORT_HOLDER["port"] = port
    ThreadingHTTPServer(("127.0.0.1", port), run_tests.H).serve_forever()

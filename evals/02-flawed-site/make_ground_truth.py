#!/usr/bin/env python3
"""Ground truth for eval 02: run the Tier B workflow (crawl, headers,
html on the homepage, links) against the flawed fixture from
tests/run_tests.py and merge. Saves ground_truth.json + work/*.json
beside this file. The merged output is what reports are graded
against; its counts are measured, never assumed.
"""
import json
import os
import subprocess
import sys
import threading
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(REPO, "website-audit", "scripts")
sys.path.insert(0, os.path.join(REPO, "tests"))
import run_tests  # noqa: E402

PORT = 8921
BASE = "http://127.0.0.1:%d" % PORT
WORK = os.path.join(HERE, "work")


def run(script, *args):
    cmd = [sys.executable, os.path.join(SCRIPTS, script), *args,
           "--allow-private", "--timeout", "5"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return proc.stdout


def save(name, text):
    with open(os.path.join(WORK, name), "w") as f:
        f.write(text)


def main():
    os.makedirs(WORK, exist_ok=True)
    run_tests.PORT_HOLDER["port"] = PORT
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), run_tests.H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        save("crawl.json", run("check_crawl.py", BASE))
        save("headers-home.json", run("check_headers.py", BASE + "/"))
        save("html-home.json", run("check_html.py", BASE + "/"))
        save("links-home.json", run("check_links.py", BASE + "/", "--delay", "0"))
        names = sorted(n for n in os.listdir(WORK) if n.endswith(".json"))
        merged = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "merge_reports.py")] +
            [os.path.join(WORK, n) for n in names],
            capture_output=True, text=True, timeout=60)
        data = json.loads(merged.stdout)
        with open(os.path.join(HERE, "ground_truth.json"), "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        print("distinct issues:", data["summary"]["distinct_issues"],
              "| by severity:", data["summary"]["distinct_issues_by_severity_hint"])
        for i in data["issues"]:
            print(" -", i["id"], i.get("severity_hint"), i.get("confidence"))
        print("not_checked:", data.get("not_checked"))
    finally:
        srv.shutdown()


if __name__ == "__main__":
    main()

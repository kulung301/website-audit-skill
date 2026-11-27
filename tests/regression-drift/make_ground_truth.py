#!/usr/bin/env python3
"""Generate ground_truth.json for the drift regression scenario.

Starts serve_fixture.py on a scratch port, runs the skill's Tier B
scripts against it exactly as SKILL.md's workflow prescribes, merges
the outputs, and saves the merged JSON next to this file. The merged
output is the single source of truth the scenario grades against:
every count and severity label a report may state is in there.

Usage: python3 make_ground_truth.py
Standard library only.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(REPO, "website-audit", "scripts")
PORT = 8917
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
    server = subprocess.Popen(
        [sys.executable, os.path.join(HERE, "serve_fixture.py"), str(PORT)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + "/", timeout=2)
                break
            except Exception:
                time.sleep(0.1)
        save("crawl.json", run("check_crawl.py", BASE))
        save("headers-home.json", run("check_headers.py", BASE + "/"))
        save("html-home.json", run("check_html.py", BASE + "/"))
        save("html-about.json", run("check_html.py", BASE + "/about"))
        save("links-home.json", run("check_links.py", BASE + "/"))
        merged = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "merge_reports.py")] +
            [os.path.join(WORK, n) for n in sorted(os.listdir(WORK))
             if n.endswith(".json")],
            capture_output=True, text=True, timeout=60)
        data = json.loads(merged.stdout)
        out = os.path.join(HERE, "ground_truth.json")
        with open(out, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        issues = data.get("issues", [])
        print("ground truth written:", out)
        print("distinct issues:", len(issues))
        for i in issues:
            print(" -", i["id"], "| severity_hint:", i.get("severity_hint"),
                  "| confidence:", i.get("confidence"),
                  "| pages:", i.get("pages_affected", i.get("count", "")))
        print("not_checked:", data.get("not_checked", data.get("coverage", {})))
    finally:
        server.terminate()


if __name__ == "__main__":
    main()

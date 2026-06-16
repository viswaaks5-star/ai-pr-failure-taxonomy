#!/usr/bin/env python3
"""Batch-run static_check.py over the corpus's policy-class dead PRs.

Reads data/prs.jsonl, maps each entry's failure_class to static_check's
--close-class, and for the policy classes {provenance, trust-gate, comms}
pins the PR's base ref and runs the harness. 'none-merged' cases are skipped
(they didn't die). quality/duplicate/process need a per-PR symbol read and
are run individually, not here.
"""
import json, subprocess
from pathlib import Path

PRS = Path("data/prs.jsonl")
CHECKOUTS = {"godotengine/godot": "repro/checkouts/godot",
             "ghostty-org/ghostty": "repro/checkouts/ghostty"}
SHORT = {"godotengine/godot": "godot", "ghostty-org/ghostty": "ghostty"}
CLASS_MAP = {
    "closed-by-provenance-rule":   "provenance",
    "closed-by-trust-gate":        "trust-gate",
    "closed-by-ai-comms-distrust": "comms",
    "closed-by-quality-judgment":  "quality",
    "superseded-or-duplicate":     "duplicate",
    "misfiled-pr":                 "process",
}
BATCH = {"provenance", "trust-gate", "comms"}

def sh(args):
    return subprocess.run(args, capture_output=True, text=True)

def main():
    rows = [json.loads(l) for l in PRS.read_text(encoding="utf-8").splitlines() if l.strip()]
    ran = 0
    for r in rows:
        repo, num = r["repo"], r["number"]
        cc = CLASS_MAP.get(r.get("failure_class", ""))
        if cc not in BATCH:
            continue
        co = CHECKOUTS.get(repo)
        if not co:
            print(f"SKIP {repo}#{num}: no checkout"); continue
        base = sh(["gh", "pr", "view", str(num), "--repo", repo,
                   "--json", "baseRefOid", "-q", ".baseRefOid"]).stdout.strip()
        if not base:
            print(f"SKIP {repo}#{num}: no base ref"); continue
        sh(["git", "-C", co, "checkout", "-q", base])
        out = f"repro/verdicts/{SHORT[repo]}-{num}.json"
        res = sh(["python3", "scripts/static_check.py", "--repo", repo, "--pr", str(num),
                  "--checkout", co, "--close-class", cc, "--out", out])
        if res.returncode == 0:
            print(res.stdout.strip()); ran += 1
        else:
            print(f"ERR {repo}#{num}: {res.stderr.strip()}")
    print(f"\n=== ran {ran} verdicts ===")

if __name__ == "__main__":
    main()

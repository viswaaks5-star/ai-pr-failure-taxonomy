"""Static-verification harness for the AI-PR failure taxonomy.

Machine-decide WHY a dead AI-PR died, deterministically, without building:
  claim-reproduced     : a technical failure is machine-confirmed
                         (diff won't apply | PR's own CI failed | a claimed API is absent at base)
  provenance-confirmed : code applies, PR CI did not fail, and the maintainer close was
                         non-correctness (provenance/trust/comms) -> "sound code, killed on policy"
  inconclusive         : neither pattern holds (a judgment/design case)
Exit: 0 verdict emitted, 2 tool/env error. repro_status is ONLY ever set from the verdict JSON.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)

def fetch_diff(repo, num, dest):
    r = sh(["gh", "pr", "diff", str(num), "--repo", repo])
    if r.returncode != 0:
        raise SystemExit(f"[2] gh pr diff failed {repo}#{num}: {r.stderr.strip()}")
    dest.write_text(r.stdout, encoding="utf-8")

# Checks whose failure is NOT a correctness signal (style/lint/sign-off/policy bots).
# A red here says nothing about whether the code is sound, so we ignore it for the
# failure verdict -- same asymmetry as a failed `git apply`.
NONCORRECTNESS_CHECK = ("style", "format", "lint", "clang-format", "docs",
                        "dco", "sign-off", "signoff", "vouch", "license", "cla")

def is_correctness_check(name):
    n = (name or "").lower()
    return not any(tok in n for tok in NONCORRECTNESS_CHECK)

def ci_conclusion(repo, num):
    r = sh(["gh", "pr", "view", str(num), "--repo", repo, "--json", "statusCheckRollup"])
    if r.returncode != 0:
        return "unknown"
    rollup = (json.loads(r.stdout or "{}").get("statusCheckRollup") or [])
    if not rollup:
        return "none"
    def failed(c):
        return (c.get("conclusion") or c.get("state") or "").upper() in (
            "FAILURE", "ERROR", "CANCELLED", "TIMED_OUT")
    # only a CORRECTNESS check failing counts as a technical failure
    if any(failed(c) and is_correctness_check(c.get("name") or c.get("context"))
           for c in rollup):
        return "failure"
    return "success"

def applies(checkout, diff_path):
    return sh(["git", "apply", "--check", str(diff_path)], cwd=checkout).returncode == 0

def symbol_absent(checkout, symbol):
    return sh(["git", "grep", "-n", symbol], cwd=checkout).returncode != 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--checkout", required=True, help="clone checked out at the pinned base ref")
    ap.add_argument("--close-class", required=True,
                    choices=["provenance", "trust-gate", "comms", "quality", "duplicate", "process"])
    ap.add_argument("--check-symbol", action="append", default=[],
                    help="claimed API that should exist at base; repeat. Absent => hallucination.")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    co = Path(a.checkout)
    with tempfile.TemporaryDirectory() as t:
        diff = Path(t) / "pr.diff"
        fetch_diff(a.repo, a.pr, diff)
        does_apply = applies(co, diff)
        missing = [s for s in a.check_symbol if symbol_absent(co, s)]
        ci = ci_conclusion(a.repo, a.pr)

    technical_fail = bool(missing) or ci == "failure"
    sound_kill = does_apply and ci in ("success", "none", "unknown") \
                 and a.close_class in ("provenance", "trust-gate", "comms")
    verdict = "claim-reproduced" if technical_fail else \
              "provenance-confirmed" if sound_kill else "inconclusive"

    rec = {"repo": a.repo, "number": a.pr, "applies": does_apply,
           "symbols_missing": missing, "pr_ci": ci, "close_class": a.close_class,
           "verdict": verdict}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec))
    sys.exit(0)

if __name__ == "__main__":
    main()

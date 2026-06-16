#!/usr/bin/env python3
"""Set repro_status in data/labels.jsonl FROM the verdict JSONs -- never by hand.

Label records are keyed by the manifest key (repo#number) as a single field.
Verdict JSONs carry repo + number separately; we rebuild the same key to match.
HAND_VERDICT overrides batch output for PRs needing a per-PR symbol read.
"""
import json
from pathlib import Path

LABELS = Path("data/labels.jsonl")
VERDICTS = Path("repro/verdicts")
KEY_FIELD = "key"   # <-- set to whatever `head -1 data/labels.jsonl | jq .` shows

HAND_VERDICT = {"godotengine/godot#101081": "claim-reproduced"}

def main():
    verdicts = {}
    for f in sorted(VERDICTS.glob("*.json")):
        v = json.loads(f.read_text(encoding="utf-8"))
        verdicts[f"{v['repo']}#{v['number']}"] = v["verdict"]
    verdicts.update(HAND_VERDICT)

    rows = [json.loads(l) for l in LABELS.read_text(encoding="utf-8").splitlines() if l.strip()]
    written = 0
    for r in rows:
        k = r.get(KEY_FIELD)
        if k in verdicts:
            r["repro_status"] = verdicts[k]
            written += 1
    LABELS.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"wrote repro_status into {written} label records")

if __name__ == "__main__":
    main()

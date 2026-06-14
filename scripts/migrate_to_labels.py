import json
from pathlib import Path
out = []
for line in Path("data/prs.jsonl.bak").read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    r = json.loads(line)
    out.append({
        "key": f'{r["repo"]}#{r["number"]}',
        "signals": r.get("signals", []),
        "signal_confidence": r.get("signal_confidence", ""),
        "evidence": r.get("evidence", {}),
        "failure_class": r.get("failure_class", "unclassified"),
        "failure_hypothesis": r.get("failure_hypothesis", ""),
        "close_reason_quote": r.get("close_reason_quote", ""),
        "repro_status": r.get("repro_status", "pending"),
        "notes": r.get("notes", ""),
    })
Path("data/labels.jsonl").write_text(
    "\n".join(json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",",":")) for o in out) + "\n",
    encoding="utf-8", newline="\n")
print(f"wrote {len(out)} label records")

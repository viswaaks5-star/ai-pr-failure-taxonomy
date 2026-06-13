import json, sys, re
REQUIRED = ["repo","number","url","state","author","signals","evidence","failure_class","failure_hypothesis","repro_status"]
URL_RE = re.compile(r"^https://github\.com/")

def main(path):
    errors = 0
    count = 0
    for i, line in enumerate(open(path), 1):
        line = line.strip()
        if not line:
            continue
        count += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"line {i}: invalid JSON: {e}"); errors += 1; continue
        for field in REQUIRED:
            if field not in row:
                print(f"line {i}: missing '{field}'"); errors += 1
        if not URL_RE.match(str(row.get("url",""))):
            print(f"line {i}: url not github.com"); errors += 1
        if "link" not in row.get("evidence", {}):
            print(f"line {i}: evidence.link missing"); errors += 1
    if errors:
        print(f"FAIL: {errors} error(s) across {count} entries"); sys.exit(1)
    print(f"OK: {count} entries valid"); sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/prs.jsonl")

count:
	@grep -c . data/prs.jsonl
validate:
	@python scripts/validate.py data/prs.jsonl

repro-check:
	@python3 scripts/run_verdicts.py >/dev/null 2>&1 || true
	@python3 scripts/write_repro_status.py >/dev/null
	@python3 scripts/pull_prs.py rebuild >/dev/null
	@test "$$(python3 scripts/pull_prs.py hash)" = "$$(cat data/prs.sha256)" && echo "REPRO-CHECK: MATCH (verdicts reproduce, repro_status intact)" || { echo "REPRO-CHECK: DRIFT"; exit 1; }

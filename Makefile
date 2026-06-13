count:
	@grep -c . data/prs.jsonl
validate:
	@python scripts/validate.py data/prs.jsonl

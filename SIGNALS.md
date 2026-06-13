# AI - suspect signal rubric (v0)

Five operational signals. A PR earns a signal only if the stated test is met, with a permalink as evidence.

-**S1 - Author discloses AI use .** The PR author states they used  AI (e.g. Ghostty's mandatory disclosure). Strongest self-reported signal.
-**S2 - Maintainer names AI.**A repo maintainer references AI in a comment or close reason. Gold standard label: the ground truth comes from the person who own the code.
-**S3 - Bot/agent author.** The PR is a known agent account (e.g. copilot-swe-agent).
-**S4 -Slop pattern.**Telltale artifacts: hallucinated/nonexistent API, untouched checklist boilerplate, fabricated test claims("all test pass" on code that doesn't compile).
**S5- New account + large confident diff.** Freshly created account opening a large, assured change with no project history.

Each logged PR record which signals fired, with a quote (<=15words) and a permalink in the evidence field.

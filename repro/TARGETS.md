# Day 3 reproduction targets — Branch B (static verification)

## Why Branch B (from the H0 query over the 40-entry corpus)
- Repo split: 27 ghostty, 13 godot. curl = 0, tldraw = 0 (Day-1 thin-vein call now hard fact).
- Of the 27 dead PRs, kill reason is overwhelmingly provenance / trust-gate / comms / design.
- The only build-exposable claims (#101081, #113175, #111027) are all Godot C++ and ALL
  decidable by `git grep` + CI-parse — no build needed.
=> Harness = "machine-decide WHY each dead PR died," not "build it and watch it break."
   Pulls the curriculum's Day-5 static_check.py forward.

## The 3 specimens (exercise BOTH verdicts, BOTH repos)
1. godotengine/godot#101081   expect: claim-reproduced     (hallucinated Performance:: method, never compiled)
2. godotengine/godot#119505   expect: provenance-confirmed (sound re-entrancy fix, 58k assertions pass; killed solely under entirely-AI rule)
3. ghostty-org/ghostty#12140  expect: provenance-confirmed (disclosed Codex PR auto-closed pre-review under vouch policy DESPITE passing checks)

## Falsification
If #101081 does NOT come out different from the other two, the harness is broken.
That contrast IS the analytical point.

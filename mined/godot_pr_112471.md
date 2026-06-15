# PR 112471 [MERGED] — Fix glow visual compatibility regression
AUTHOR: Rudra-ravi

## BODY
Reverts the default value of Environment.glow_hdr_threshold from 0.0 back to 1.0 to restore the expected glow appearance in existing projects.

The default was inadvertently changed from 1.0 to 0.0 in PR #110077, which caused glow effects to render dramatically different across all rendering methods (Forward+, Mobile, and GL Compatibility). This broke backward compatibility with existing projects like the Kenney 3D Platformer starter kit.

Setting the value back to 1.0 aligns with documented recommendations and restores visual consistency.

Fixes #112469

<!--
Please target the `master` branch in priority.

Relevant fixes are cherry-picked for stable branches as needed by maintainers.

To speed up the contribution process and avoid CI errors, please set up pre-commit hooks locally:
https://contributing.godotengine.org/en/latest/engine/guidelines/code_style.html
-->


## COMMENTS
--- Repiteo:
Thanks! Congratulations on your first merged contribution! 🎉 

--- vv221:
I could find nothing in Godot contributing guidelines about AI contributions, then I found this accepted patch.

Is Godot open to LLM / agentic AI contributions?

--- akien-mga:
@vv221 See https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions

AI-assisted contributions are acceptable if they're disclosed and the main author is a human who used an AI to understand a problem, and not an AI who used a human's hardware to vibe code.

This one wasn't disclosed, and we didn't noticed that it was AI generated, as the OP seemed human written and the change was trivial and discussed in the issue already. We missed that this was authored by @claude and not the PR opened (@claude is now blocked from contributing to Godot). In hindsight, this should have been flagged and rejected.

--- vv221:
> AI-assisted contributions are acceptable (…)

Thank you for the confirmation.


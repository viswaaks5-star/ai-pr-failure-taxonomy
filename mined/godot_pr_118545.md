# PR 118545 [CLOSED] — Prevent re-entrant Main::iteration() in ProgressDialog::_update_ui
AUTHOR: dsarno

## BODY
Fixes #118544

**Note to maintainers:** This is not an AI slop PR..  I'm the lead maintainer on the 8,000 star Unity-MCP project. I do use LLMs to build (like many engineers), but I also make sure changes are minimal, follow project culture, and are well tested. I rebuilt Godot with the fix and tested it thoroughly. Just thought I'd let you know.  At unity-mcp, we get a ton of slop too, so anyway, hello from a real human!

## What happens

`ProgressDialog::_update_ui()` calls `Main::iteration()` with no re-entrancy guard. This runs a full frame cycle including `_process()` on all `@tool` nodes. If any plugin's `_process()` triggers a save (directly or indirectly), the call chain recurses: `_save_scene_with_preview` → `EditorProgress::step()` → `_update_ui()` → `Main::iteration()` → `_process()` → `save_scene()` → ... The stack overflows after ~1000 frames and the editor crashes (SIGSEGV).

## Fix

Adds a static `is_iterating` guard to `_update_ui()` — if `Main::iteration()` is already running from a prior `_update_ui()` call up the stack, the nested call is skipped. Same pattern as `prevent_recursive_process_hack` in `EditorFileSystem` (#73214 / #54864).

## Test plan

- [ ] Enable the MRP plugin from #118544 (a `@tool` plugin that calls `EditorInterface.save_scene()` from `_process()`)
- [ ] Without fix: editor crashes within seconds (SIGSEGV, stack overflow from 1000+ recursive `_process()` frames)
- [ ] With fix: editor stays alive, no recursion — `_update_ui()` returns early on re-entrant calls


## COMMENTS
--- AThousandShips:
Closing as this PR violates our contribution guidelines on AI generated code


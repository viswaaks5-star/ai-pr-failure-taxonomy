# PR 119809 [CLOSED] — GDScript: Fix null-mutex crash in GDScript and GDScriptInstance destructors on shutdown
AUTHOR: superherointj

## BODY
Fixes #119279 (and duplicates #119799, #112480, gdUnit4#1151).

## What changed

Three null-singleton guards in `modules/gdscript/gdscript.cpp`:

1. **`GDScriptInstance::~GDScriptInstance()`** — Use manual `lock()`/`unlock()` instead of scoped `MutexLock`, so the mutex is held for the entire destructor body even with the null-singleton check. Addresses review feedback from @bruvzg on the previous version (PR #119800).

2. **`GDScript::cancel_pending_functions()`** — Early return when `GDScriptLanguage::get_singleton()` is null. All pending functions have been cleared by `GDScriptLanguage::finish()`.

3. **`GDScript::~GDScript()`** — Null-singleton guard for the `script_list.remove_from_list()` mutex block.

## Why this is safe

After `GDScriptLanguage::finish()` has been called (which happens before the singleton is destroyed), no GDScript code executes. The mutex is not needed during single-threaded shutdown when all script data structures have already been cleared.

## Testing

- Reproduction project from #119279 validated before patch: all methods exit with code 134 (SIGABRT)
- After fix: all methods exit cleanly with code 0
- Validated on both 4.6.3-stable and master

## Previous iteration

This is a corrected version of PR #119800 which was closed. The previous version used `MutexLock` inside an `if` block, which created a scope-narrowing issue (the lock was released at the end of the `if` block before the destructor body ran). This version uses manual lock/unlock as suggested by @bruvzg.

## AI disclosure

This contribution was authored with assistance from an AI coding agent (OpenCode+DeepSeek-v4-Flash), which helped with the root cause analysis, reproduction, and patch drafting. All code changes were reviewed and tested by the author.

## COMMENTS
--- AThousandShips:
Was the code written by you or entirely by an LLM? Please see our [guidelines](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions)


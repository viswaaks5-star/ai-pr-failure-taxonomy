# PR 118384 [CLOSED] — Fix race condition in threaded resource loading with shared subresources
AUTHOR: Infiland

## BODY
## Summary

- Refine deadlock detection in `WorkerThreadPool::wait_for_task_completion` to allow collaborative waiting when the awaited task is already running on a different pool thread, instead of unconditionally returning `ERR_BUSY`
- Add a `load_claimed` flag to `ThreadLoadTask` to prevent concurrent execution of `_run_load_task` for the same task
- Add a post-load status check in `_run_load_task` to safely discard results if another thread completed the task first

Fixes #118085

## Details

When two threads load scenes that share a subresource (e.g. a VisualShader) via `load_threaded_request`, the deadlock prevention in `WorkerThreadPool::wait_for_task_completion` returns `ERR_BUSY` whenever a pool thread waits for an older task. The `ResourceLoader` responds by calling `_run_load_task` with the same `ThreadLoadTask`, causing both threads to load the resource concurrently. The resource gets added to `ResourceCache` during loading (before properties are fully set), so the second thread finds the partially-loaded resource and modifies it concurrently, crashing on non-thread-safe `HashMap`/`RBMap` operations.

The root issue is that the deadlock detection conflates two cases:
1. Task is queued but not executing -- genuinely dangerous to wait
2. Task is executing on another thread -- safe to wait collaboratively

The fix checks `task->pool_thread_index` (already maintained under `task_mutex`) to distinguish these cases. When the task is running on a different thread, we fall through to `_wait_collaboratively` instead of returning `ERR_BUSY`. For the remaining edge case where the task is queued, the `load_claimed` flag and post-load guard prevent concurrent execution.

## Test plan

- [ ] Build the engine in debug mode
- [ ] Run the MRP from the issue (concurrent `load_threaded_request` for scenes sharing a VisualShader) repeatedly to verify no crashes
- [ ] Run existing `tests/core/threads/test_worker_thread_pool.cpp` tests to check for regressions
- [ ] Verify `DEV_ASSERT` at `resource_loader.cpp:900` still passes (task status is `THREAD_LOAD_LOADED` or `THREAD_LOAD_FAILED` after wait)

For this particular summary, an LLM was used to write the PR description https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions

## COMMENTS
--- akien-mga:
Thanks for contributing.
Did you use AI to author this PR? If so it needs to be disclosed: https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions

I'm suspicious due to the verbosity of the PR description and the "Test plan" which seems to outline what you should have done to validate the LLM's suggestions...

--- Infiland:
> Thanks for contributing. Did you use AI to author this PR? If so it needs to be disclosed: https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions
> 
> I'm suspicious due to the verbosity of the PR description and the "Test plan" which seems to outline what you should have done to validate the LLM's suggestions...

Yeah, I did use it to author it, I'll edit the PR's description to mention it

--- hpvb:
Changes to the PR are not reflected in the PR description, the latest changes also don't fix the problem. 

Closing this.


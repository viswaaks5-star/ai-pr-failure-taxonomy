# PR 118669 [CLOSED] — [Windows] Guard HDR callbacks against destroyed windows
AUTHOR: shaun0927

## BODY
Fixes #118672

## Summary

Follow-up on #118339. `DisplayServerWindows::_get_screen_hdr_data` and the WinRT-deferred callback `_winrt_adv_color_info_cb` access `windows[p_window]` without the `windows.has(...)` guard that every other public method on `DisplayServerWindows` already uses. Because `windows[]` auto-inserts a default `WindowData` on miss (non-const) or hits UB (const), a callback that fires after the window is gone — or a public HDR call against an already-closed `WindowID` — leaks an entry or crashes.

Per @bruvzg's review feedback, this PR places the guard at the API boundary — the public HDR methods that own the `WindowID` lookup — rather than inside the helper, so the pattern matches the rest of the class. The deferred callback keeps its own guard since it owns the entry path coming back in from the WinRT dispatcher.

## Changes

`platform/windows/display_server_windows.cpp`:

- Add `ERR_FAIL_COND(!windows.has(p_id))` to `_winrt_adv_color_info_cb`.
- Add `ERR_FAIL_COND_V(!windows.has(p_window), false)` to `window_is_hdr_output_supported`.
- Add `ERR_FAIL_COND(!windows.has(p_window))` to `window_request_hdr_output`, `window_set_hdr_output_reference_luminance`, and `window_set_hdr_output_max_luminance`.

The originally proposed `controller.ShutdownQueueAsync().get()` change in `winrt_utils.cpp` was **dropped**: @bruvzg confirmed it would deadlock since `destroy_queue` runs on the main thread after the event pump has already stopped, so `.get()` would never return. The token is revoked per-window in `destroy_wd` before the queue tears down, so no callback can fire across the destructor in practice.

## Testing

Reproduced (1) by cycling HDR on/off via Windows Settings on a secondary monitor while a second editor window is dragged onto/off that monitor and closed during the toggle. Without the guards, `windows[p_id]` auto-inserts a fresh `WindowData` (visible as a leaked entry in debug builds) and `_update_hdr_output_for_window` runs against a default-initialized struct.

No behaviour change outside the error paths.

---

> [!NOTE]
> 🤖 AI Disclosure
>
> AI assistance (Claude) was used to scan the diff range introduced by #118339 and to draft this patch and PR description. The findings, the placement of the guards, and the rejection of the `ShutdownQueueAsync().get()` approach were verified by hand against the surrounding code and against @bruvzg's review feedback before pushing.


## COMMENTS
--- shaun0927:
Thanks @bruvzg for the review.

Pushed a follow-up that addresses both points:

- Moved the guard from `_get_screen_hdr_data` to the four public HDR methods you listed (`window_is_hdr_output_supported`, `window_request_hdr_output`, `window_set_hdr_output_reference_luminance`, `window_set_hdr_output_max_luminance`), so the check sits at the API boundary like the rest of the class.
- Dropped the `controller.ShutdownQueueAsync().get()` change — your point about the main thread / stopped event pump is right, it would have deadlocked. The per-window token revoke in `destroy_wd` already handles the practical race, so the original concern was moot.

The deferred callback `_winrt_adv_color_info_cb` still keeps its own guard, since it's the entry point from the WinRT dispatcher back into Godot.

Let me know if there are other call sites I missed.

--- AThousandShips:
Superseded by:
* https://github.com/godotengine/godot/pull/118680


# PR 118966 [CLOSED] — 🤖 macOS: Discard OS-injected phantom mouseMoved events that break fullscreen UI clicks
AUTHOR: gregod-com

## BODY
## Summary

On **macOS 26 (Tahoe)**, clicking any editor UI button (Run, Stop, 2D/3D/Script tabs, etc.) while the editor is in fullscreen mode silently fails. The button visually reacts to the press but does not activate on release. Keyboard shortcuts for the same actions work fine.

## Root cause

After every real `mouseDown:` in fullscreen, macOS injects one or two synthetic `NSEvent` `mouseMoved:` events with **stale, off-cursor coordinates**. These phantom events reach `BaseButton::gui_input` motion handling, which calls `has_point(position)` on the stale position — evaluating to `false` — and clears `pressing_inside`. On release, the guard `press_attempt && pressing_inside` then fails, so the button never activates.

Instrumentation confirmed that **Godot does not issue any `CGWarpMouseCursorPosition` call** on this code path; the events are purely OS-generated (a macOS Tahoe regression). The phantoms are reliably identified by: `subtype == NSEventSubtypeMouseEvent (0)`, `deviceID == 0`, `delta == (0, 0)`.

## Fix

Discard `mouseMoved:` events matching that signature when the window is in fullscreen mode. A stationary cursor never emits a real `mouseMoved` event, so the guard is safe.

## Testing

- Confirmed bug present on macOS 26 / M1 Max with Godot 4.6-stable and master.
- Confirmed fix resolves Run, Stop, 2D/3D/Script tabs, and ConfirmationDialog buttons in fullscreen.
- Windowed mode unaffected.

> [!INFO] *AI disclosure*: This contribution was authored by an autonomous AI agent (GitHub Copilot), on behalf of the user Gregor Pirolt, who reproduced the bug, guided the investigation, and verified the fix.

## COMMENTS
--- AThousandShips:
We do not accept PRs entirely written by LLMs or other generative AI tools, and we do not accept PRs submitted by autonomous agents at all

--- gregod-com:
> We do not accept PRs entirely written by LLMs or other generative AI tools, and we do not accept PRs submitted by autonomous agents at all

I see. Given that it is a tiny change, does it make sense that I recreate the MR as my personal contribution?
It is after all mostly a cosmetic / QoL change.

--- Ivorforce:
Yes, you can resubmit the PR if you use your own words, and adhere to our [pull request rules](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html).

--- AThousandShips:
Assuming the code is your own and not written by an LLM or other generative AI tool


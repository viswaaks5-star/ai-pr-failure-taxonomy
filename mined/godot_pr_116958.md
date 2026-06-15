# PR 116958 [CLOSED] — Windows: Auto-enable single-window mode in virtualized GPU environments
AUTHOR: RJAudas

## BODY
## Summary

Automatically enable single-window (embedded sub-windows) mode on Windows when running in a virtualized GPU environment where Vulkan device creation has failed.

### Changes

- **VM detection** (`display_server_windows.cpp`): When the rendering driver is OpenGL and no Vulkan rendering context exists, check `IsProcessorFeaturePresent(PF_VIRT_FIRMWARE_ENABLED)` to detect hypervisor environments. If all conditions are met, set `embedding_subwindows_recommended = true`.
- **DisplayServer API** (`display_server.h`): Added `embedding_subwindows_recommended` protected bool and `is_embedding_subwindows_recommended()` public getter to the base `DisplayServer` class.
- **Startup check** (`main.cpp`): Check `is_embedding_subwindows_recommended()` alongside the existing single-window conditions to auto-enable embedded sub-windows.
- **WM_ERASEBKGND** (`display_server_windows.cpp`): Always return 1 (suppress default erase) to reduce flicker during window resize/repaint.

### Motivation

In Hyper-V GPU paravirtualization (GPU-PV) environments with NVIDIA GPUs, Vulkan device creation fails entirely (`VK_ERROR_INITIALIZATION_FAILED`), forcing the engine to use OpenGL. With OpenGL, all windows share a single rendering context via `wglMakeCurrent`. When multiple windows exist (dialogs, popups, sub-windows), the constant context switching causes severe UI flickering due to limitations in the paravirtualized GPU driver.

Single-window mode embeds all sub-windows within the main window, eliminating the need for `wglMakeCurrent` context switching and completely resolving the flickering.

### Detection Logic

The detection is intentionally narrow to avoid false positives:
1. **OpenGL is active** (`rendering_driver == "opengl3"`).
2. **No Vulkan context exists** (`rendering_context == nullptr`), indicating Vulkan failed.
3. **Running in a hypervisor** (`IsProcessorFeaturePresent(PF_VIRT_FIRMWARE_ENABLED)`).

This combination targets specifically GPU-PV environments with broken Vulkan support. Bare-metal users, VMs with working Vulkan, and VMs using software rendering are unaffected.

### Testing

Tested on Hyper-V VM with paravirtualized NVIDIA RTX 4090:
- Before: Severe UI flickering when any dialog or sub-window opens
- After: No flickering; all sub-windows embedded in main window
- Bare-metal: No behavior change (Vulkan works, detection does not trigger)

### Related

PR #116957 improves the Vulkan error logging that helps diagnose these environments.

### Other approaches tried

Before arriving at the single-window auto-detection fix, several other approaches were investigated and tested on the same Hyper-V GPU-PV environment. None resolved the flickering:

- **`DwmFlush()` after swap** — Called `DwmFlush()` per-window in `swap_buffers` and also as a single end-of-frame flush. Had no measurable effect on the flickering because the issue is in `wglMakeCurrent` context switching, not in swap timing or DWM composition.
- **Suppressing `WM_ERASEBKGND`** — Returning 1 from `WM_ERASEBKGND` (kept in this PR) reduces repaint flicker slightly but does not address the core multi-window GL context switching issue on its own.
- **Deferred `SwapBuffers`** — Rendered all viewports first, then called `SwapBuffers` for all windows at the end of the frame. Did not help because the flickering occurs during `wglMakeCurrent` calls between windows, not during the swap itself.
- **Disabling vsync** — No effect on the flickering.
- **Vulkan extension reduction/retry** — Attempted stripping non-essential Vulkan extensions and retrying `vkCreateDevice` (now in PR #116957). The GPU-PV driver fails with `VK_ERROR_INITIALIZATION_FAILED` regardless of which extensions are requested, even with swapchain only. Vulkan is fundamentally unsupported in this environment.
- **ANGLE (OpenGL-over-DirectX)** — Could theoretically bypass the `wglMakeCurrent` issue by using DirectX under the hood, but requires pre-built static libraries not included in the Godot repository and was not feasible to test.
- **`--single-window` command-line flag** — Manually passing `--single-window` confirmed that single-window mode eliminates the flickering entirely, which led to implementing automatic detection in this PR.

## COMMENTS
--- Ivorforce:
Closing as this PR has all the hallmarks of an AI generated description without an AI use disclosure. This violates our [rules on AI assisted PRs](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html).

If you wish to continue contributing, please familiarize yourself with our [PR rules](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html) and [engine contribution guidelines](https://contributing.godotengine.org/en/latest/engine/guidelines/index.html).

--- RJAudas:
Just a FYI this was created by AI with my help over hours. And I checked the CONTRIBUTING.md file and it had no mention of the AI rules. Sorry I missed them. You should consider updating the CONTRIBUTING.md. I'll put in a bug for the flickering. Thank you for your time.

--- Ivorforce:
> Just a FYI this was created by AI with my help over hours. And I checked the CONTRIBUTING.md file and it had no mention of the AI rules. Sorry I missed them. You should consider updating the CONTRIBUTING.md. I'll put in a bug for the flickering. Thank you for your time.

You're right, `CONTRIBUTING.md` does not effectively link to our PR rules right now. It does link to the contributing docs, but I can see how you could have missed this info. We'll adjust it asap.

We do appreciate the effort of your work to help the project. Please read the rules I linked. You can re-submit your work with appropriate descriptions and disclosure afterwards.

--- RJAudas:
Just to close the loop. I respect the policy: "The use of AI to contribute to Godot is discouraged, and contributions made entirely by AI are prohibited.". I've got 20+ years enterprise development experience including work on rendering projects. But this fix/change was entirely driven by AI and had I known that was not acceptable I wouldn't have posted the change, sorry. I'm tinkering with godot to try my hand at making some fun games for my daughter. Saw a problem, thought in this AI world I just could fix and submit. But I now can see the dangers of fly by night AI patches and why you would reject them. So no harm no foul.


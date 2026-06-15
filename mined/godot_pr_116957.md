# PR 116957 [CLOSED] — Vulkan: Improve vkCreateDevice error logging and add extension retry
AUTHOR: RJAudas

## BODY
## Summary

Improve error diagnostics and resilience when `vkCreateDevice` fails.

### Changes

**Better error logging:**
- When `vkCreateDevice` fails, log the actual `VkResult` error name (e.g., `VK_ERROR_INITIALIZATION_FAILED`) and the full list of requested extensions, instead of a generic error message.
- Added 4 missing `VkResult` error code strings to `get_vulkan_result()`: `VK_ERROR_INITIALIZATION_FAILED`, `VK_ERROR_EXTENSION_NOT_PRESENT`, `VK_ERROR_FEATURE_NOT_PRESENT`, `VK_ERROR_INCOMPATIBLE_DRIVER`.

**Extension retry on failure:**
- If `vkCreateDevice` fails, retry with non-essential extensions stripped (ray tracing, VRS, synchronization2, Vulkan memory model, device fault).
- If still failing, retry with only required extensions (swapchain).
- This helps environments like Hyper-V GPU-PV where the driver may advertise extensions it cannot actually support.

### Motivation

In GPU paravirtualization environments (e.g., Hyper-V GPU-PV with NVIDIA GPUs), `vkCreateDevice` fails with `VK_ERROR_INITIALIZATION_FAILED` even though the physical device is enumerated successfully. The current error message gives no indication of the VkResult or which extensions were requested, making debugging difficult. The retry logic gives the engine a chance to succeed with reduced functionality rather than falling back to OpenGL entirely.

### Testing

Tested on Hyper-V VM with paravirtualized NVIDIA RTX 4090:
- Before: Generic error `Condition err != VK_SUCCESS is true` with no details
- After: Detailed error `vkCreateDevice failed with error VK_ERROR_INITIALIZATION_FAILED (-3). Requested 19 extension(s): [...]`
- Retry attempts are logged with `WARN_PRINT` before falling back

## COMMENTS
--- Ivorforce:
Closing as this PR has all the hallmarks of an AI generated description without an AI use disclosure. This violates our [rules on AI assisted PRs](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html).

If you wish to continue contributing, please familiarize yourself with our [PR rules](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html) and [engine contribution guidelines](https://contributing.godotengine.org/en/latest/engine/guidelines/index.html).


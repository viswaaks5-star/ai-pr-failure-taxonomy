# PR 117913 [MERGED] — Fix behavior of `window_is_hdr_output_supported` for Wayland and adjust warnings.
AUTHOR: allenwp

## BODY
### What problem(s) does this PR solve?

1. `DisplayServerWayland::window_is_hdr_output_supported` returns `true` when the rendering device does not support HDR output. This behaviour is incorrect and does not match the behaviour of other display servers.

2. If Godot is compiled with `RD_ENABLED` not defined or `rendering_device == nullptr`, the `rendering_device->has_feature(RenderingDevice::Features::SUPPORTS_HDR_OUTPUT)` checks will never be run and the code assumes that HDR output is supported, which is the opposite behaviour of how this should be written.

### What is the rationale for the approach used in this PR?

The problem is resolved by simply adding a check to the `DisplayServerWayland::window_is_hdr_output_supported` function so it matches other display servers.

In addition to this change, I have adjusted some errors to be warnings and improved some of the warning messages.

Finally, because the functions that enable HDR output do not check if the rendering device supports HDR output, I have slightly changed the `window_request_hdr_output` logic to fail to request HDR output when `rendering_device` is `nullptr` or `RD_ENABLED` is not defined. This is safer logic that ensures its impossible for HDR output to be successfully requested when the rendering device does not support HDR output.

### Was generative AI (LLM AI) used to create a portion of this PR?

No.

### Are there any parts of this PR that you are uncertain of or require special attention from reviewers?

No, but please double check that my logic statements are correct.

## COMMENTS
--- allenwp:
cc @ArchercatNEO

--- Repiteo:
Thanks!


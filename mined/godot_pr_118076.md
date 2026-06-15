# PR 118076 [MERGED] — [Apple, Wayland] HDR Output: Emit window events when HDR state changes
AUTHOR: allenwp

## BODY
**This is a followup PR to #115666.** The original PR's commit has been included in this PR.

### What problem(s) does this PR solve?

- Parent PR #115666 adds events for Windows, but does not add events for Apple and Wayland. This PR adds these events.
- Similar to the parent PR: scripts must poll `Window.get_output_max_linear_value()` ever frame, which is inefficient because it normally does not change until the user changes their screen brightness, for example.
- #118079 needs these changes to show HDR info of the game window without polling constantly.

### What is the rationale for the approach used in this PR?

Just like #115666, this allows scripts on all platforms to change scripts that used to be:

``` GDScript
func _process(_delta: float) -> void:
	var output_max_linear_value = get_window().get_output_max_linear_value()
	# Do something with output_max_linear_value
```

Into something more efficient like this:

``` GDScript
func _enter_tree() -> void:
	var window: Window = get_window()
	window.output_max_linear_value_changed.connect(_on_output_max_linear_value_changed)
	_on_output_max_linear_value_changed(window.get_output_max_linear_value())


func _exit_tree() -> void:
	get_window().output_max_linear_value_changed.disconnect(_on_output_max_linear_value_changed)


func _on_output_max_linear_value_changed(output_max_linear_value: float) -> void:
	# Do something with output_max_linear_value
```

### Was generative AI (LLM AI) used to create a portion of this PR?

No.

### Are there any parts of this PR that you are uncertain of or require special attention from reviewers?

- It may be more convenient to test this PR with #118079 because this followup PR makes use of the signal introduced by this PR.
- For Apple, I renamed `void DisplayServerMacOSEmbedded::send_window_event(...)` to  `virtual void DisplayServerMacOSEmbedded::send_window_event_by_id(...)` and moved it to the base class to allow `DisplayServerMacOS` to use it as well. As a part of this, I changed `DisplayServerMacOS::send_window_event(...)` to be `const`, but I could instead change `virtual void send_window_event_by_id(...)` to be non-`const` if that's preferable.
- Let me know if I should squash the original PR and add a co-author if that's preferable to merging the two PRs separately, one after the other.

I've tested this to find it works well on iOS, macOS, and Fedora KDE plasma.

## COMMENTS
--- allenwp:
@ArchercatNEO requesting review from you as well as @stuartcarnie if you want to review this. Feel free to use the followup PR #118079 for testing, as it uses this PR's signal.

--- allenwp:
Oh, I completely forgot about #116134! Thanks, indeed it would be better to detect changes of luminance values by simply always firing the event when we get a `ColorProfileMessage`.

And yes, we should also fire the event any time that `window_get_hdr_output_enabled` has changed.

But on this subject... Is it possible for Wayland (or any other platform) to get into a state where `RenderingContextDriver::window_get_hdr_output_enabled(...)` would return `true` when the window is actually rendering in SDR mode? (For example, if the attempt to change to HDR mode has failed.)

As far as I can tell, `_window_update_hdr_state(...)` or equivalent on other platforms is the only place that `window_set_hdr_output_enabled` is modified, but it must always be kept in sync with the actual mode...

--- ArchercatNEO:
If enabling HDR fails in the vulkan driver, then yes `RenderingContextDriverVulkan::window_get_hdr_output_enabled` would keep returning true unless the DisplayServer (currently only wayland) re-disabled HDR rendering for that window (which it currently doesn't do).

Unless Android either guarantees that the HDR formats we want are supported in some other way, it should probably also check to make sure enabling HDR didn't fail. I read enough to know our minimum version of D3D12 is required to support our HDR formats so Windows is not at risk but I don't know enough about metal to know if enabling HDR could fail.

--- allenwp:
> Happy with the changes to Wayland code!

Thanks!

> If enabling HDR fails in the vulkan driver, then yes `RenderingContextDriverVulkan::window_get_hdr_output_enabled` would keep returning true unless the DisplayServer (currently only wayland) re-disabled HDR rendering for that window (which it currently doesn't do).

This was a bug. Do the changes that I pushed fix this bug?

> Out of curiosity, will this PR be updated to also include Android?

No, Android has outstanding issues and probably won't be merged for 4.7, but hopefully this PR can be merged for 4.7.

--- ArchercatNEO:
> > If enabling HDR fails in the vulkan driver, then yes `RenderingContextDriverVulkan::window_get_hdr_output_enabled` would keep returning true unless the DisplayServer (currently only wayland) re-disabled HDR rendering for that window (which it currently doesn't do).
> 
> This was a bug. Do the changes that I pushed fix this bug?

I believe so, if for whatever reason the rendering context is using `NONLINEAR_SRGB` we can be sure it's rendering in SDR and if it's in `EXT_LINEAR` we can be sure it's in HDR. This should disable hdr within the rendering context.

--- allenwp:
> I checked the Apple (embedded and macOS) changes and they look good to me. This is a great addition.

@stuartcarnie there was an issue in Wayland that we just discussed where `rendering_context->window_set_hdr_output_enabled(...)` was called in the DisplayServer's `update_hdr_state` function, but later when the surface was attempted to be made into an HDR surface it could fail. And if it failed, `rendering_context->window_set_hdr_output_enabled(...)` was never called and would be left in a bad state where it Godot would report `hdr_output_enabled == true` when in fact the surface was an SDR surface.

I've updated this PR to address that issue for Wayland by calling `rendering_context->window_set_hdr_output_enabled(...)` any time changing the surface has failed.

Does this sort of problem exist on any of the Apple platforms?

--- stuartcarnie:
> but later when the surface was attempted to be made into an HDR surface it could fail.

No, we should be fine. The surface on Apple already exists (`CA::MetalLayer`), we just set a boolean property that we want it to present EDR content.

--- Repiteo:
Thanks!


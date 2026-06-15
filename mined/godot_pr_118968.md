# PR 118968 [MERGED] — Fix GPU validation errors due to area light LUT format
AUTHOR: CookieBadger

## BODY
Bugsquad edit: Fixes #118930

GPU validation currently seems to throw some errors about the area light lookup table sampler2Ds not having a `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_LINEAR_BIT` set.
Update: I now changed both lookup table textures to have RGBAF format, since on some GPUs, RGBF does not support linear filtering. This fixes the validation error. 
There also was a crash when setting a texture on an area light with `--gpu-validation` on Vulkan, due to `gaussian_blur` being called without `p_8bit_dst`, which this PR fixes. Further validation errors that occur with global illumination independent of area lights remain unaffected.


## COMMENTS
--- AThousandShips:
Seems you forgot to disclose your AI use, have you forgotten to so on other PRs as well?

--- CookieBadger:
@AThousandShips ah, the hint in the commit message is new. I do have copilot enabled to help me perform similar steps quicker, e.g. rename or add a parameter, but I never generate entire sections (that would never work for rendering code).

--- AThousandShips:
Seems extremely invasive, and very confusing for maintainers to have a co-author that didn't write the code 😆 (probably best to use established and less invasive tools for that I'd say)

--- CookieBadger:
yeah, quite bold to claim a contribution when basically all it did was copy-paste the same line I wrote over 1:1for the second texture. I'll see if I can disable that...

--- CookieBadger:
Encountering an Engine crash when assigning an area light texture during `CanvasItem::_redraw_callback()`. Error message:
```Exception thrown at 0x00007FFFE67079DA in godot.windows.editor.dev.x86_64.exe: Microsoft C++ exception: std::system_error at memory location 0x00000072207F8120.
Unhandled exception at 0x00007FFFE67079DA in godot.windows.editor.dev.x86_64.exe: Microsoft C++ exception: std::system_error at memory location 0x00000072207F8120. 
```

In Visual Studio 2022, the Line throwing the error reads:

```c++
_STD _Throw_Cpp_error(_RESOURCE_DEADLOCK_WOULD_OCCUR);
```

(C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\include\mutex)

Error does not happen for omni light projector textures.

The crash seems to be triggered by the following validation error:

```
VALIDATION - Message Id Number: 20145586 | Message Id Name: Undefined-Value-StorageImage-FormatMismatch-ImageView
	vkCmdDispatch(): the storage image descriptor [VkDescriptorSet 0x633b000000633b[RID:702115483746631], Set 3, Binding 0, Index 0] is accessed by a OpTypeImage 
that has a Format operand Rgba16f (equivalent to VK_FORMAT_R16G16B16A16_SFLOAT) which doesn't match the VkImageView 0x63380000006338[RID:702106893818272 View] format (VK_FORMAT_R8G8B8A8_UNORM). 
Any loads or stores with the variable will produce undefined values to the whole image (not just the texel being accessed).
Spec information at https://docs.vulkan.org/spec/latest/chapters/textures.html#textures-format-validation
	Objects - 3
		Object[0] - VK_OBJECT_TYPE_PIPELINE, Handle 1588794302137765, Name "RID:3096671420574"
		Object[1] - VK_OBJECT_TYPE_DESCRIPTOR_SET, Handle 27930893880419131, Name "RID:702115483746631"
		Object[2] - VK_OBJECT_TYPE_IMAGE_VIEW, Handle 27927595345535800, Name "RID:702106893818272 View"
```

need to put a pin on this for today, maybe somebody can have a look where that `Rgba16f` operand is coming from.

--- blueskythlikesclouds:
That validation error appears to be happening because you don't set `p_8bit_dst` to `true` when calling `gaussian_blur` in `update_area_light_atlas`.

--- CookieBadger:
@blueskythlikesclouds thanks, that's indeed the issue! 

On another note, I noticed similar issues with format mismatches across the board, see https://github.com/godotengine/godot/issues/119012

Also, invalid format issues appear even before area lights in 4.7.dev4 and likely prior as well when opening a scene with SDFGI or VoxelGI:
```
ERROR: drivers/vulkan/rendering_context_driver_vulkan.cpp:672 - Vulkan Debug Report: object - 1327110534726839
  ERROR: vkCmdDispatch(): the sampled image descriptor [VkDescriptorSet 0x44e800000044e8, Set 1, Binding 0, Index 0] VkImageViewType is VK_IMAGE_VIEW_TYPE_2D_ARRAY but the OpTypeImage has (Dim = 2D) and (Arrayed = 0).
  ERROR: Either fix in shader or update the VkImageViewType to VK_IMAGE_VIEW_TYPE_2D.
  ERROR: The Vulkan spec states: If a VkImageView is accessed as a result of this command, then the image view's viewType must match the Dim operand of the OpTypeImage as described in Compatibility Between SPIR-V Image Dimensions and Vulkan ImageView Types (https://docs.vulkan.org/spec/latest/chapters/dispatch.html#VUID-vkCmdDispatch-viewType-07752)
```

I'm not sure the change in this pull request (change DDS format from RGB to RGBA) is actually a good solution, as these issues might need tackling on a lower level.

--- blueskythlikesclouds:
> I'm not sure the change in this pull request (change DDS format from RGB to RGBA) is actually a good solution, as these issues might need tackling on a lower level.

It should be for now. This format doesn't appear to be used anywhere else in RD.

--- CookieBadger:
@blueskythlikesclouds the .dds is not used anywhere else, correct, but the RGB formats are used in many places for all sorts of textures, and whereever they are sampled linearly, vulkan throws validation errors when the validation layers are enabled.

If you have an intel GPU, you can try and run any scene with SDFGI or bake a lightmap and find those texture problems.

The PR increases the size of the LUT by a couple of kB just for this extra channel, which is a suboptimal workaround. If possible it'd be preferable if #119012 could be fixed first and the GI problems investigated, independent from area lights.

--- blueskythlikesclouds:
Why should that be fixed first? That's a different error from Intel iGPUs not supporting linear filtering on RGB32_FLOAT formats.

I don't agree this is as suboptimal as you think. These few KBs are basically nothing. If anything, it's possible the GPU has an easier time loading the RGBA32_FLOAT format thanks to each pixel being 16 byte aligned.

--- CookieBadger:
ok, then here we go :)

--- Repiteo:
Thanks!


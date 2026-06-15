# PR 116454 [MERGED] —  Decouple RenderingServer from as much of the codebase as possible, moving enums to a new `RSE` namespace
AUTHOR: akien-mga

## BODY
- Helps address #111218.
- ~Depends on #115623, ignore the first 3 "GLES3" commits.~ (Merged.)
- ~Depends on #116693, ignore the first `windows.h` commit.~ (Merged.)

A number of headers in the codebase included `rendering_server.h` just for some enum definitions. This means that any change to `rendering_server.h` or one of its dependencies would trigger a massive incremental rebuild.

With these changes, we decouple a number of classes from `rendering_server.h`, greatly speeding up incremental rebuilds for that area.

On my machine, compiling with `scons p=linux dev_build=yes dev_mode=yes fast_unsafe=yes linker=mold`, this reduces incremental compilation time after an edit of `rendering_server.h` from **2m57s to 1m17s** (i.e. 57% reduction, 100s saved).
It doesn't seem to affect the time it takes to build everything from scratch.

The changes are unfortunately somewhat intrusive, but after a few iterations and discussion on [RC](https://chat.godotengine.org/channel/devel?msg=jpdygWGCM8HFy4o28), I think what we land on isn't too bad. Instead of using RenderingServer enums with `RS::EnumName` or `RS::CONSTANT_NAME`, you replace `RS` by `RSE` and replace the `rendering_server.h` include by `rendering_server_enums.h` (which is a much smaller file with almost no dependencies).

> [!WARNING]
> This PR might have some adverse impacts on the PR backlog in two ways that we'll have to watch out for:
> - The removal of `rendering_server.h` and its dependencies as transitive includes in a large part of the codebase means that some headers that were previously taken from granted now need to be included explicitly. So some PRs may fail compiling if merged after this and not rebased prior to merging.
> - A lot of files are changed so there might be a bunch of merge conflicts.

> [!NOTE]
> **AI disclosure:** I designed and tested all changes myself, but I did use Copilot midway through to automate some of the busywork of moving all enums to a new file and adapting the rest of the codebase for the changes (it basically ran a couple vibe coded python scripts, based on initial work I had already done myself to validate the design). I reviewed all changes and spent a few additional ~hours~ days fixing remaining compilation errors and optimizing includes further. So I don't consider any of the code in this PR to be "AI generated", it's the same I would have done myself. The PR description is verbose but that's all written by me, there's just a lot to explain about this PR :sweat_smile: 

## Changes

~### 1. Fix `windows.h` include ordering mess with `platform_gl.h`~

- Superseded by #116693.

<details>
<summary>Previous description</summary>

Needs review from @bruvzg. I put this as the first commit as it's independent from the rest, but it was actually needed after the big commit adding `RSE`. I didn't look too deeply into why I was getting a `windows.h`/`object.h` conflict on ConnectFlags, possibly some reordering of includes or the fact that due to reduced transitive includes, `typedefs.h` would no longer be included after `windows.h`.

Moving the `#undef`s to `platform_config.h` and removing the `#pragma once` might be a bit controversial and/or risky, so I can also drop that commit and try to find another more localized approach to fix this issue. (E.g. duplicating the `#undef`s in `platform_gl.h`.)

</details>

### 2. ClassDB: Allow binding bitfield enums and constants from separate namespaces

Prerequisite for the rest, as RenderingServer has one BitField enum (`ArrayFormat`), and I moved some regular constants / anonymous enums to RSE too which require allowing and stripping `RSE::` in the `BIND_CONSTANT` call. I adapted the changes from #115963.

### 3. Move RenderingServer enums to a dedicated RenderingServerEnums (`RSE`) namespace

The main part of this PR. It creates `servers/rendering/rendering_server_enums.h` and moves all enums from `rendering_server.h` to it. I asked Copilot to ensure they're in the same order as they were in `rendering_server.h`, with similar area-defining comments. That might need double-checking.

The rest of the changes is necessary to make things compile:
- Replace the use of `RS::` / `RenderingServer::` with `RSE::`
- Replace explicit or implicit includes to `rendering_server.h` by `rendering_server_enums.h`
- Add a bunch of other headers here and there which are now needed due to not including `rendering_server.h` transitively everywhere, which means some places now need an explicit include for `Engine`, `OS`, `RBMap`/`RBSet`, etc. This is good and what we want.
- In particular, one goal I had was to remove `rendering_server.h` from all `.h` files, and especially ones in `scene`. It was notably included in `canvas_item.h` and `visual_instance_3d.h`, which means that all GUI, 2D, and 3D nodes included it transitively. Another significant removal is from `material.h`.
- I added a few `STATIC_ASSERT_INCOMPLETE_TYPE(class, RenderingServer);` checks in critical classes (CanvasItem, VisualInstance3D, Viewport, Window, SceneTree) to make sure we don't include `rendering_server.h` explicitly or transitively in their headers or dependencies.

~### 4. Move `RS::SurfaceData::LOD` to a separate file, to remove RS dependency in `mesh.h`~

This was merged into the commit decoupling MeshStorage from RS, as it supersedes it.

<details>
<summary>Previous description</summary>

`mesh.h` was the last `scene` header not covered in the previous commit, because it also depended on a struct nested deeply in RenderingServer.

So I created another namespace and file, RenderingServerTypes in `rendering_server_types.h` to put a new `RenderingServerTypes::SurfaceDataLOD` struct in there, and use that one in `mesh.h`, `rendering_server.h`, and the few other places which used that struct explicitly.

I kept this separate for review/discussion. It removes another \~23s from the incremental rebuild time for me, so it's definitely worth it, but the implementation can be adapted.

</details>

### 5. Decouple RenderingServer from XR/OpenXR headers

After all the above, I noticed that `xr_server.h` and `openxr_api.h` still included `rendering_server.h` directly, for some methods implemented directly in the header with `__FORCE_INLINE__`. I moved them to the .cpp files and dealt with the subsequent chain of missing includes, but this needs to be reviewed and ideally tested by @godotengine/xr. Was this `__FORCE_INLINE__` really key to performance, or are we confident it will be optimized well enough by the compiler anyway with the methods implemented in the .cpp?

This change removed another \~8s from the incremental rebuild time.

### 6. Decouple RenderingServer from ServersDebugger

Since I was on a roll, I dealt with the last remaining low-hanging fruit, also by moving the `RS::FrameProfileArea` struct to `RenderingServerTypes`. This made no impact on the rebuild time, `servers_debugger.h` isn't a hot include currently.
But I kept it anyway as I think we want to have a strict policy of not including `rendering_server.h` in a header if we can reasonably avoid it.

*Edit:* After edits this is the first commit creating RenderingServerTypes, for a change without a major impact. it's just because the big impactful change to `SurfaceData::LOD` was moved to a later commit.

### 7. Move BlitToScreen to RenderingServerTypes, fixing XRInterface cyclic dependency trap

XRInterface was forward-declaring BlitToScreen, forcing all implementations to include `renderer_compositor.h` explicitly (in practice, my previous change removed it as a transient include so things started to break). Looking into it, I tried to remove the forward-declare and everything broke because RendererCompositor includes RenderingMethod which includes... XRInterface. Nasty coupling there.

I moved BlitToScreen to the new RenderingServerTypes so it can now be included where needed without adding coupling. This only saves around 1s of incremental rebuild time, but it's mostly a code quality fix.

### 8. Remove `RenderingServer::map_scaling_option_to_stretch_mode` and cleanup boot splash code

This is a fixup to #109596, we should have allowed `project_settings.cpp` to be tightly coupled with `rendering_server.h`. The helper method isn't particularly needed in the first place, I just inlined it where it's used in the compositor, and hardcoded values in `project_settings.cpp` because it's unlikely to change and this is deprecated compat code anyway. Not much impact on compile time.

### 9. Misc dependency improvements for files depending on `rendering_server.h`

I did another pass on most remaining reverse dependencies of `rendering_server.h` as described in https://github.com/godotengine/godot/pull/116454#issuecomment-3926817152, and fixed what I could find. Notably:

- Remove direct `rendering_server.h` includes in a few places where it's not actually needed. Notably a big impact from removing it in `rasterizer_dummy.h`
- Cleanup some overreaching includes in a few place that would pull in `rendering_server.h` needlessly.
- Misc cleanup of includes / forward-declares in the files I was looking at, not all related to `rendering_server.h` specifically.

### 10. Move `RS::ShaderNativeSourceCode` to RenderingServerTypes to reduce dependencies on RS

Reduces the dependency on RS from MaterialStorage and paves the way for more internal renderer decoupling.

### 11. Minimize includes in `renderer_compositor.h`

`RenderingCompositor` is a virtual interface that ends up included in quite a few places, but it can totally use forward-declares instead of coupling all the rendering classes. This means that it's now the responsibility of the user to include the headers for the members it wants to use.

### 12. Decouple MeshStorage from RenderingServer

This one is a big one, as it decouples not only internal rendering components from each other, but also removes the dependency on RS from `mesh.h`, which is included in a lot of the codebase. So it saves a lot of time on incremental rebuilds.

### 13. Decouple TextureStorage from RenderingServer

More internal rendering code refactoring to decouple things and reduce which renderer files need to be recompiled when changing e.g. `rendering_server.h`.

### 14. Decouple RasterizerDummy from RenderingServer and DisplayServer

Looking at what were still reverse dependencies of `rendering_server.h`, I noticed that a bunch of DisplayServers would get recompiled when modifying it because they create `RasterizerDummy`. RasterizerDummy would directly include a lot of the renderer classes, so I moved those to pointers so they can be forward-declared.

### 15. Move RenderingMethod::RenderInfo to RenderingServerTypes

Helps decouple a number of files from `rendering_method.h`, which includes XRInterface and would lead to XRInterface being available way beyond where it should be.

## Future work

Some other potential changes I noted down while working on this, to be explored in other PRs:

- `RenderingServer::get_singleton()->get_video_adapter_name()` is used in a few places just to print it to stdout, we could reduce RS dependencies by moving it somewhere else.
- MeshStorage only depends on RS for SurfaceData and MeshInfo.
- MaterialStorage only depends on RS for ShaderNativeSourceCode.
- RS only includes DisplayServer for WindowID and VSyncMode. Prime candidate for further refactoring.
- All remaining direct includes of `rendering_server.h` in headers seem to be in rendering code. It's tightly coupled by design, so it's not surprising, but maybe we can uncouple things a bit and avoid recompiling all of `servers/rendering/` all the time.

```
$ rg -g'*.h' "include .*rendering_server\.h" --sort=path -l
servers/rendering/rendering_server_default.h
```

## COMMENTS
--- bruvzg:
Maybe we should limit all these `windows.h` undefs only to the places where it is used, and replace `#include <windows.h>` with a wrapper header, something like this (tested with GCC and CLANG and is seem to work fine):

```diff
diff --git a/platform/windows/crash_handler_windows.h b/platform/windows/crash_handler_windows.h
index 358d0ce3cf..6bf8ecece4 100644
--- a/platform/windows/crash_handler_windows.h
+++ b/platform/windows/crash_handler_windows.h
@@ -30,8 +30,7 @@
 
 #pragma once
 
-#define WIN32_LEAN_AND_MEAN
-#include <windows.h>
+#include "platform/windows/windows_inc.h"
 
 // Crash handler exception only enabled with MSVC
 #if defined(DEBUG_ENABLED)
diff --git a/platform/windows/display_server_windows.h b/platform/windows/display_server_windows.h
index a942c8bb68..24df6d4fcd 100644
--- a/platform/windows/display_server_windows.h
+++ b/platform/windows/display_server_windows.h
@@ -62,9 +62,8 @@
 #include <io.h>
 #include <cstdio>
 
-#define WIN32_LEAN_AND_MEAN
+#include "platform/windows/windows_inc.h"
 #include <shobjidl.h>
-#include <windows.h>
 #include <windowsx.h>
 
 // WinTab API
diff --git a/platform/windows/os_windows.h b/platform/windows/os_windows.h
index 453f333449..4efde62dbb 100644
--- a/platform/windows/os_windows.h
+++ b/platform/windows/os_windows.h
@@ -49,10 +49,9 @@
 #include <shellapi.h>
 #include <cstdio>
 
-#define WIN32_LEAN_AND_MEAN
+#include "platform/windows/windows_inc.h"
 #include <dwrite.h>
 #include <dwrite_2.h>
-#include <windows.h>
 #include <windowsx.h>
 
 #ifdef DEBUG_ENABLED
diff --git a/platform/windows/platform_config.h b/platform/windows/platform_config.h
index cebd1a7027..22c22f778e 100644
--- a/platform/windows/platform_config.h
+++ b/platform/windows/platform_config.h
@@ -28,17 +28,6 @@
 /* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                 */
 /**************************************************************************/
 
-// No header guards, we want this to be always be included to undef windows.h conflicts.
+#pragma once
 
 #include <malloc.h>
-
-// windows.h badly defines a lot of stuff we'll never use. Undefine it.
-#undef min // override standard definition
-#undef max // override standard definition
-#undef ERROR // override (really stupid) wingdi.h standard definition
-#undef DELETE // override (another really stupid) winnt.h standard definition
-#undef MessageBox // override winuser.h standard definition
-#undef Error
-#undef OK
-#undef CONNECT_DEFERRED // override from Windows SDK, clashes with Object enum
-#undef MONO_FONT
diff --git a/platform/windows/platform_gl.h b/platform/windows/platform_gl.h
index fc7ba064a5..3d4a05c0db 100644
--- a/platform/windows/platform_gl.h
+++ b/platform/windows/platform_gl.h
@@ -48,6 +48,3 @@
 #endif
 
 #include "thirdparty/glad/glad/gl.h"
-
-// Include last to undef a bunch of windows.h conflicts.
-#include "platform_config.h"
diff --git a/platform/windows/tts_windows.h b/platform/windows/tts_windows.h
index d841ac4cc2..8cc96b6902 100644
--- a/platform/windows/tts_windows.h
+++ b/platform/windows/tts_windows.h
@@ -41,8 +41,7 @@
 #include <winnls.h>
 #include <cwchar>
 
-#define WIN32_LEAN_AND_MEAN
-#include <windows.h>
+#include "platform/windows/windows_inc.h"
 
 class TTS_Windows {
 	List<DisplayServer::TTSUtterance> queue;
diff --git a/platform/windows/windows_inc.h b/platform/windows/windows_inc.h
new file mode 100644
index 0000000000..aab67001d5
--- /dev/null
+++ b/platform/windows/windows_inc.h
@@ -0,0 +1,45 @@
+/**************************************************************************/
+/*  windows_inc.h                                                         */
+/**************************************************************************/
+/*                         This file is part of:                          */
+/*                             GODOT ENGINE                               */
+/*                        https://godotengine.org                         */
+/**************************************************************************/
+/* Copyright (c) 2014-present Godot Engine contributors (see AUTHORS.md). */
+/* Copyright (c) 2007-2014 Juan Linietsky, Ariel Manzur.                  */
+/*                                                                        */
+/* Permission is hereby granted, free of charge, to any person obtaining  */
+/* a copy of this software and associated documentation files (the        */
+/* "Software"), to deal in the Software without restriction, including    */
+/* without limitation the rights to use, copy, modify, merge, publish,    */
+/* distribute, sublicense, and/or sell copies of the Software, and to     */
+/* permit persons to whom the Software is furnished to do so, subject to  */
+/* the following conditions:                                              */
+/*                                                                        */
+/* The above copyright notice and this permission notice shall be         */
+/* included in all copies or substantial portions of the Software.        */
+/*                                                                        */
+/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,        */
+/* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF     */
+/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. */
+/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY   */
+/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,   */
+/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE      */
+/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                 */
+/**************************************************************************/
+
+#pragma once
+
+#define WIN32_LEAN_AND_MEAN
+#include <windows.h>
+
+// windows.h badly defines a lot of stuff we'll never use. Undefine it.
+#undef min // override standard definition
+#undef max // override standard definition
+#undef ERROR // override (really stupid) wingdi.h standard definition
+#undef DELETE // override (another really stupid) winnt.h standard definition
+#undef MessageBox // override winuser.h standard definition
+#undef Error
+#undef OK
+#undef CONNECT_DEFERRED // override from Windows SDK, clashes with Object enum
+#undef MONO_FONT
diff --git a/thirdparty/glad/EGL/eglplatform.h b/thirdparty/glad/EGL/eglplatform.h
index 6786afd90b..4c2d3b1605 100644
--- a/thirdparty/glad/EGL/eglplatform.h
+++ b/thirdparty/glad/EGL/eglplatform.h
@@ -55,10 +55,7 @@ typedef void *EGLNativePixmapType;
 typedef void *EGLNativeWindowType;
 
 #elif defined(_WIN32) || defined(__VC32__) && !defined(__CYGWIN__) && !defined(__SCITECH_SNAP__) /* Win32 and WinCE */
-#ifndef WIN32_LEAN_AND_MEAN
-#define WIN32_LEAN_AND_MEAN 1
-#endif
-#include <windows.h>
+#include "platform/windows/windows_inc.h"
 
 typedef HDC     EGLNativeDisplayType;
 typedef HBITMAP EGLNativePixmapType;

```

--- akien-mga:
I checked the SCons output for which `.cpp` files are compiled with an incremental rebuild after editing `rendering_server.h` after the previous state of this PR:

<details>

```
core/config/project_settings.cpp
core/io/resource_loader.cpp
drivers/egl/egl_manager.cpp
drivers/gles3/effects/copy_effects.cpp
drivers/gles3/effects/cubemap_filter.cpp
drivers/gles3/effects/feed_effects.cpp
drivers/gles3/effects/glow.cpp
drivers/gles3/effects/post_effects.cpp
drivers/gles3/environment/fog.cpp
drivers/gles3/environment/gi.cpp
drivers/gles3/rasterizer_canvas_gles3.cpp
drivers/gles3/rasterizer_gles3.cpp
drivers/gles3/rasterizer_scene_gles3.cpp
drivers/gles3/shader_gles3.cpp
drivers/gles3/storage/light_storage.cpp
drivers/gles3/storage/material_storage.cpp
drivers/gles3/storage/mesh_storage.cpp
drivers/gles3/storage/particles_storage.cpp
drivers/gles3/storage/render_scene_buffers_gles3.cpp
drivers/gles3/storage/texture_storage.cpp
drivers/gles3/storage/utilities.cpp
drivers/unix/os_unix.cpp
editor/animation/animation_player_editor_plugin.cpp
editor/animation/animation_track_editor_plugins.cpp
editor/audio/audio_stream_editor_plugin.cpp
editor/editor_interface.cpp
editor/editor_node.cpp
editor/export/shader_baker_export_plugin.cpp
editor/gui/progress_dialog.cpp
editor/import/audio_stream_import_settings.cpp
editor/inspector/editor_inspector.cpp
editor/inspector/editor_preview_plugins.cpp
editor/inspector/editor_resource_picker.cpp
editor/inspector/editor_resource_preview.cpp
editor/project_manager/project_dialog.cpp
editor/register_editor_types.cpp
editor/scene/2d/path_2d_editor_plugin.cpp
editor/scene/2d/polygon_2d_editor_plugin.cpp
editor/scene/2d/tiles/tile_atlas_view.cpp
editor/scene/2d/tiles/tile_data_editors.cpp
editor/scene/2d/tiles/tiles_editor_plugin.cpp
editor/scene/3d/camera_3d_editor_plugin.cpp
editor/scene/3d/lightmap_gi_editor_plugin.cpp
editor/scene/3d/material_3d_conversion_plugins.cpp
editor/scene/3d/node_3d_editor_gizmos.cpp
editor/scene/3d/node_3d_editor_plugin.cpp
editor/scene/canvas_item_editor_plugin.cpp
editor/scene/material_editor_plugin.cpp
editor/scene/texture/texture_region_editor_plugin.cpp
editor/script/script_text_editor.cpp
editor/shader/editor_native_shader_source_visualizer.cpp
editor/shader/shader_globals_editor.cpp
editor/shader/text_shader_editor.cpp
editor/shader/visual_shader_editor_plugin.cpp
main/main.cpp
main/performance.cpp
modules/basis_universal/image_compress_basisu.cpp
modules/betsy/image_compress_betsy.cpp
modules/betsy/register_types.cpp
modules/camera/camera_feed_linux.cpp
modules/csg/csg_shape.cpp
modules/godot_physics_3d/godot_soft_body_3d.cpp
modules/gridmap/editor/grid_map_editor_plugin.cpp
modules/gridmap/grid_map.cpp
modules/jolt_physics/objects/jolt_soft_body_3d.cpp
modules/ktx/texture_loader_ktx.cpp
modules/lightmapper_rd/lightmapper_rd.cpp
modules/mobile_vr/mobile_vr_interface.cpp
modules/navigation_3d/editor/navigation_obstacle_3d_editor_plugin.cpp
modules/noise/noise_texture_2d.cpp
modules/noise/noise_texture_3d.cpp
modules/openxr/extensions/openxr_android_thread_settings_extension.cpp
modules/openxr/extensions/openxr_composition_layer_extension.cpp
modules/openxr/extensions/openxr_fb_foveation_extension.cpp
modules/openxr/extensions/openxr_frame_synthesis_extension.cpp
modules/openxr/extensions/openxr_visibility_mask_extension.cpp
modules/openxr/extensions/platform/openxr_opengl_extension.cpp
modules/openxr/extensions/platform/openxr_vulkan_extension.cpp
modules/openxr/openxr_api.cpp
modules/openxr/openxr_api_extension.cpp
modules/openxr/openxr_interface.cpp
modules/openxr/scene/openxr_visibility_mask.cpp
modules/raycast/raycast_occlusion_cull.cpp
modules/raycast/register_types.cpp
modules/text_server_adv/text_server_adv.cpp
modules/webxr/webxr_interface_js.cpp
platform/linuxbsd/os_linuxbsd.cpp
platform/linuxbsd/wayland/display_server_wayland.cpp
platform/linuxbsd/x11/display_server_x11.cpp
scene/2d/back_buffer_copy.cpp
scene/2d/canvas_group.cpp
scene/2d/canvas_modulate.cpp
scene/2d/cpu_particles_2d.cpp
scene/2d/gpu_particles_2d.cpp
scene/2d/light_2d.cpp
scene/2d/light_occluder_2d.cpp
scene/2d/line_2d.cpp
scene/2d/navigation/navigation_agent_2d.cpp
scene/2d/navigation/navigation_obstacle_2d.cpp
scene/2d/navigation/navigation_region_2d.cpp
scene/2d/node_2d.cpp
scene/2d/parallax_2d.cpp
scene/2d/parallax_layer.cpp
scene/2d/path_2d.cpp
scene/2d/polygon_2d.cpp
scene/2d/skeleton_2d.cpp
scene/2d/tile_map_layer.cpp
scene/2d/visible_on_screen_notifier_2d.cpp
scene/3d/camera_3d.cpp
scene/3d/cpu_particles_3d.cpp
scene/3d/decal.cpp
scene/3d/fog_volume.cpp
scene/3d/gpu_particles_3d.cpp
scene/3d/gpu_particles_collision_3d.cpp
scene/3d/label_3d.cpp
scene/3d/light_3d.cpp
scene/3d/lightmap_gi.cpp
scene/3d/mesh_instance_3d.cpp
scene/3d/navigation/navigation_agent_3d.cpp
scene/3d/navigation/navigation_link_3d.cpp
scene/3d/navigation/navigation_obstacle_3d.cpp
scene/3d/navigation/navigation_region_3d.cpp
scene/3d/node_3d.cpp
scene/3d/occluder_instance_3d.cpp
scene/3d/path_3d.cpp
scene/3d/physics/collision_object_3d.cpp
scene/3d/physics/collision_shape_3d.cpp
scene/3d/physics/ray_cast_3d.cpp
scene/3d/physics/shape_cast_3d.cpp
scene/3d/physics/soft_body_3d.cpp
scene/3d/reflection_probe.cpp
scene/3d/skeleton_3d.cpp
scene/3d/sprite_3d.cpp
scene/3d/visible_on_screen_notifier_3d.cpp
scene/3d/visual_instance_3d.cpp
scene/3d/voxel_gi.cpp
scene/debugger/runtime_node_select.cpp
scene/debugger/scene_debugger.cpp
scene/gui/code_edit.cpp
scene/gui/color_picker_shape.cpp
scene/gui/control.cpp
scene/gui/item_list.cpp
scene/gui/label.cpp
scene/gui/line_edit.cpp
scene/gui/menu_button.cpp
scene/gui/nine_patch_rect.cpp
scene/gui/rich_text_label.cpp
scene/gui/text_edit.cpp
scene/gui/texture_progress_bar.cpp
scene/gui/tree.cpp
scene/main/canvas_item.cpp
scene/main/canvas_layer.cpp
scene/main/scene_tree.cpp
scene/main/shader_globals_override.cpp
scene/main/viewport.cpp
scene/main/window.cpp
scene/register_scene_types.cpp
scene/resources/2d/capsule_shape_2d.cpp
scene/resources/2d/circle_shape_2d.cpp
scene/resources/2d/concave_polygon_shape_2d.cpp
scene/resources/2d/convex_polygon_shape_2d.cpp
scene/resources/2d/rectangle_shape_2d.cpp
scene/resources/2d/segment_shape_2d.cpp
scene/resources/2d/separation_ray_shape_2d.cpp
scene/resources/2d/tile_set.cpp
scene/resources/2d/world_boundary_shape_2d.cpp
scene/resources/3d/fog_material.cpp
scene/resources/3d/mesh_library.cpp
scene/resources/3d/primitive_meshes.cpp
scene/resources/3d/sky_material.cpp
scene/resources/3d/world_3d.cpp
scene/resources/animated_texture.cpp
scene/resources/blit_material.cpp
scene/resources/camera_attributes.cpp
scene/resources/camera_texture.cpp
scene/resources/canvas_item_material.cpp
scene/resources/compositor.cpp
scene/resources/compressed_texture.cpp
scene/resources/curve_texture.cpp
scene/resources/dpi_texture.cpp
scene/resources/drawable_texture_2d.cpp
scene/resources/environment.cpp
scene/resources/external_texture.cpp
scene/resources/font.cpp
scene/resources/gradient_texture.cpp
scene/resources/image_texture.cpp
scene/resources/immediate_mesh.cpp
scene/resources/material.cpp
scene/resources/mesh.cpp
scene/resources/mesh_texture.cpp
scene/resources/multimesh.cpp
scene/resources/particle_process_material.cpp
scene/resources/placeholder_textures.cpp
scene/resources/portable_compressed_texture.cpp
scene/resources/shader.cpp
scene/resources/sky.cpp
scene/resources/style_box_flat.cpp
scene/resources/style_box_line.cpp
scene/resources/style_box_texture.cpp
scene/resources/texture.cpp
scene/resources/texture_rd.cpp
scene/resources/visual_shader.cpp
scene/resources/visual_shader_nodes.cpp
scene/resources/world_2d.cpp
scene/theme/theme_db.cpp
servers/camera/camera_feed.cpp
servers/camera/camera_server.cpp
servers/debugger/servers_debugger.cpp
servers/display/display_server.cpp
servers/display/display_server_headless.cpp
servers/movie_writer/movie_writer.cpp
servers/register_server_types.cpp
servers/rendering/dummy/storage/material_storage.cpp
servers/rendering/dummy/storage/mesh_storage.cpp
servers/rendering/dummy/storage/utilities.cpp
servers/rendering/instance_uniforms.cpp
servers/rendering/renderer_canvas_cull.cpp
servers/rendering/renderer_canvas_render.cpp
servers/rendering/renderer_compositor.cpp
servers/rendering/renderer_rd/cluster_builder_rd.cpp
servers/rendering/renderer_rd/effects/bokeh_dof.cpp
servers/rendering/renderer_rd/effects/copy_effects.cpp
servers/rendering/renderer_rd/effects/debug_effects.cpp
servers/rendering/renderer_rd/effects/fsr.cpp
servers/rendering/renderer_rd/effects/fsr2.cpp
servers/rendering/renderer_rd/effects/luminance.cpp
servers/rendering/renderer_rd/effects/metal_fx.cpp
servers/rendering/renderer_rd/effects/motion_vectors_store.cpp
servers/rendering/renderer_rd/effects/resolve.cpp
servers/rendering/renderer_rd/effects/roughness_limiter.cpp
servers/rendering/renderer_rd/effects/smaa.cpp
servers/rendering/renderer_rd/effects/sort_effects.cpp
servers/rendering/renderer_rd/effects/ss_effects.cpp
servers/rendering/renderer_rd/effects/taa.cpp
servers/rendering/renderer_rd/effects/tone_mapper.cpp
servers/rendering/renderer_rd/effects/vrs.cpp
servers/rendering/renderer_rd/environment/fog.cpp
servers/rendering/renderer_rd/environment/gi.cpp
servers/rendering/renderer_rd/environment/sky.cpp
servers/rendering/renderer_rd/forward_clustered/render_forward_clustered.cpp
servers/rendering/renderer_rd/forward_clustered/scene_shader_forward_clustered.cpp
servers/rendering/renderer_rd/forward_mobile/render_forward_mobile.cpp
servers/rendering/renderer_rd/forward_mobile/scene_shader_forward_mobile.cpp
servers/rendering/renderer_rd/renderer_canvas_render_rd.cpp
servers/rendering/renderer_rd/renderer_compositor_rd.cpp
servers/rendering/renderer_rd/renderer_scene_render_rd.cpp
servers/rendering/renderer_rd/shader_rd.cpp
servers/rendering/renderer_rd/storage_rd/light_storage.cpp
servers/rendering/renderer_rd/storage_rd/material_storage.cpp
servers/rendering/renderer_rd/storage_rd/mesh_storage.cpp
servers/rendering/renderer_rd/storage_rd/particles_storage.cpp
servers/rendering/renderer_rd/storage_rd/render_scene_buffers_rd.cpp
servers/rendering/renderer_rd/storage_rd/render_scene_data_rd.cpp
servers/rendering/renderer_rd/storage_rd/texture_storage.cpp
servers/rendering/renderer_rd/storage_rd/utilities.cpp
servers/rendering/renderer_scene_cull.cpp
servers/rendering/renderer_scene_occlusion_cull.cpp
servers/rendering/renderer_scene_render.cpp
servers/rendering/renderer_viewport.cpp
servers/rendering/rendering_light_culler.cpp
servers/rendering/rendering_server.cpp
servers/rendering/rendering_server_default.cpp
servers/rendering/rendering_shader_container.cpp
servers/rendering/shader_compiler.cpp
servers/rendering/shader_language.cpp
servers/rendering/storage/mesh_storage.cpp
servers/rendering/storage/render_scene_buffers.cpp
servers/text/text_server.cpp
servers/xr/xr_interface_extension.cpp
servers/xr/xr_server.cpp
servers/xr/xr_vrs.cpp
tests/display_server_mock.cpp
tests/scene/test_arraymesh.cpp
tests/test_main.cpp
```

</details>

I reviewed them all to see how to further minimize dependencies on RenderingServer and made a bunch of improvements.

I left out the two big chunks of `drivers/gles3/` and `servers/rendering/` where the coupling is much stronger and which will require a dedicated pass (doesn't have to be in this PR).

After my last batch of changes, we're down to roughly 1m12s for incremental rebuilds (goes down further by a few seconds with #112041). The following files are no longer recompiled when changing `rendering_server.h`:

```
core/config/project_settings.cpp
drivers/unix/os_unix.cpp
editor/gui/progress_dialog.cpp
modules/betsy/register_types.cpp
modules/mobile_vr/mobile_vr_interface.cpp
modules/openxr/openxr_interface.cpp
modules/raycast/raycast_occlusion_cull.cpp
modules/raycast/register_types.cpp
scene/3d/physics/collision_shape_3d.cpp
servers/camera/camera_server.cpp
```

I'll add details about the new commits to the OP.

--- akien-mga:
Last bunch of commits starts decoupling the inner parts of `servers/rendering/` some more. Everything was massively intertwined, I made a good dent but there's still some work to do possibly.

I'm now down to **1m03s** for an incremental rebuild of `rendering_server.h`.

--- akien-mga:
> Maybe we should limit all these `windows.h` undefs only to the places where it is used, and replace `#include <windows.h>` with a wrapper header, something like this (tested with GCC and CLANG and is seem to work fine):

I gave this a try on the `master` branch (https://github.com/akien-mga/godot/tree/windows-leaner-and-meaner), but the problem is that `windows.h` is also included by thirdparty code, so we'd need to patch those as well. And there are other Windows headers that can be included directly that also define some of these.

So I get this issue for example:
```
In file included from /usr/x86_64-w64-mingw32/sys-root/mingw/include/windows.h:77,
                 from thirdparty/glad/EGL/eglplatform.h:61,
                 from ./thirdparty/glad/glad/egl.h:327,
                 from platform/windows/platform_gl.h:47,
                 from drivers/egl/egl_manager.h:36,
                 from drivers/egl/egl_manager.cpp:31:
./core/object/object.h:574:17: error: expected identifier before numeric constant
  574 |                 CONNECT_DEFERRED = 1,
      |                 ^~~~~~~~~~~~~~~~
```

--- blueskythlikesclouds:
I feel like [091312a](https://github.com/godotengine/godot/commit/091312ac31b8d2e83710a449efd954d80a928e6c) should be added to the git blame ignore list.

--- akien-mga:
Alright, I think this is ready.

`rendering_server.h` is now only included in a single header, `rendering_server_default.h`, which inherits from it.
Otherwise it's only included in `.cpp` files, and I checked that they all use `RenderingServer::` or `RS::` explicitly. `rendering_server_default.h` itself is only included in `.cpp` files, so we should no longer have transitive includes of `rendering_server.h` through common headers.

Incremental recompilation time after changing `rendering_server.h` on my laptop is brought down from 3m to just under 1m.


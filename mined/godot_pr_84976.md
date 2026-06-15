# PR 84976 [MERGED] — Acyclic Command Graph for Rendering Device
AUTHOR: DarioSamo

## BODY
### Background

@reduz proposed the idea a while ago of refactoring RenderingDevice to automatically build a graph out of the commands submitted to the class (outlined [here](https://gist.github.com/reduz/980b9b2547d57e6a915b2bb7e1e76e08)). The first stepping stone towards implementing this was @RandomShaper's PR (#83452) that splits the commands into easily serializable parameters. Therefore, merging this PR will require merging that PR first (and if you wish to review this, only look at my individual commit after Pedro's changes).

### Improvements

This PR makes the following improvements towards implementing @reduz's idea.

- **RenderingDevice**'s complexity has been drastically reduced as it no longer needs to solve pipeline barriers or layout transitions for pretty much all its functionality. This responsibility has been delegated to a new class called **RenderingDeviceGraph**.
- Overall the total amount of `vkCmdPipelineBarrier` calls has been reduced immensely. On average I've noticed a reduction of about 60-80% of the total amount of barrier calls in a frame when compared to `master`.
- **RenderingDeviceGraph** is capable of reordering commands based on the dependency between the resources used to push the submitted commands to be processed as early as possible. This gives the driver much better chances of parallelizing the work effectively.
- **RenderingDeviceGraph** will group as many possible barriers as possible in **'levels'** depending on the usage of the resources. These barriers are submitted before the commands of the level are processed to perform any layout or synchronization barriers that are required.
- **RenderingDevice**'s API has been simplified as some parameters are no longer required.
  - Barrier bitmasks are gone. They no longer serve any purpose.
  - Draw list and compute list overlapping no longer needs to be specified.
  - 'Split draw lists' are gone as they can be automatically recorded by the graph instead, and has been shown to be viable already (although disabled behind an experimental macro for now).
  - Draw lists no longer need to specify their initial and final actions in excruciating detail. The operations are much simpler now. Load, clear or discard for initial. Store and discard for final. The detail behind the original action no longer serves any purpose, as the graph will automatically skip any transitions that are not required if commands that use the same image layout are chained together (e.g. render passes).
  - Draw lists no longer need to specify storage textures as it's not required at all.
- Both Forward+ and Mobile have been adapted to use the new API and have overall resulted in a net removal of code complexity that is no longer required due to the graph automatically solving what it was doing already.
- A lot of existing Vulkan synchronization errors caused by the current barrier system have been solved automatically by the graph.

### Implementation
Since commands need to be deferred until later for reordering, everything submitted to RD is serialized into a large uint8 vector that grows as much as necessary. The capacity of all these vectors is reused across recordings to avoid reallocation as much as possible. The recorded commands are the bare minimum the **RenderingDeviceDriver** needs to execute the command after reordering is performed.

As expected, this PR will add CPU overhead that was not there before due to the additional time spent recording commands and reordering. While there's a very obvious optimization that is indicated in the TODO list that is pending, the rest of the extra work won't be as easy to overcome. This extra cost can also be offset tremendously by using secondary command buffers, which is pending to be enabled in the PR as soon as the issue described in the TODO is figured out.

### Compatibility breakage
- **RenderingDevice**'s binary compatibility is not guaranteed as expected due to a lot of arguments being removed from the functions. I've provided compatibility wrappers as required, although I'm not quite clear if they work as intended yet.
- If the compatibility wrappers work as intended, there should be no need to change the behavior of the code dependent on RD: pretty much most of the time the additional detail that was provided to the functions is just ignored as the graph can solve it on its own.
- In some cases it is possible compatibility breaks because the graph performs additional layers of validation as to whether some operations are allowed. The validation that **RenderingDeviceGraph** includes:
  - Checking whether the same resource is used with different usages in the same command. This was found to be the case already with a couple of effects that used the indirect buffer as both dispatch and storage, leading to UB.
  - Checking if multiple slices of the same resource in different usages are used in the same command and have overlap. This is not allowed as the layout transitions are impossible to solve effectively and can lead to race conditions in the GPU. Luckily, such a case was not found in the existing rendering code as far as I could find, but if some code runs into this it means it has to be fixed on the user side and not on the graph.

### Performance improvements
GPU performance improvements are expected across the board as long as the CPU overhead isn't slowing the game down (which should go down with the future immutable change). The performance improvements will also vary depending on how much the particular IHV was suffering from inefficient barrier usage. One area that will particularly benefit is projects using GPU particles, as their processing will be much more parallelized than it was before.

At least on an NVIDIA 3090ti I've noticed around an overall ~10% frame time improvement in several projects, with potential bigger wins in platforms like AMD that can parallelize effectively on single queue or mobile hardware that does not handle barriers as gracefully as NVIDIA does.

### Future improvements
These will be researched after this PR is merged as a second iteration.
- Dedicated transfer queue for resources that use the setup command buffer that can run in parallel and synchronize when it's time to process the drawing commands.
- Support for multiple graphics and compute queues that will split the work of the graph to support parallelization on hardware that can take advantage of it more effectively (like NVIDIA).

## TODO
- [x] Debug broken uniform set in TPS demo (will be fixed in Pedro's PR soon).
- [x] Debug strange memory usage increase far beyond what should be expected.
- [x] Update documentation to match the new API.
- [x] Fix the C# glue error that is not getting generated properly for some reason due to the RD API change.
- [x] Double check if MSAA is working on Forward+ and Mobile.
- [x] Attempt new mutable/immutable tracker design that does not require explicit flags from the engine. This requires working out a way to refresh the trackers used by vertex, index and uniform set arrays once those resources turn into mutables. All dependencies must be made mutable.
- [x] Debug strange issue in NVIDIA where the editor will show up completely black when using secondary command buffers depending on the contents of the draw list. This currently blocks secondary command buffers from being enabled. I've been unable to determine the root of the issue so far. (Postponed until we get feedback from NVIDIA)

_Production edit: closes godotengine/godot-roadmap#29_

## COMMENTS
--- DarioSamo:
Opening this for review. We won't take any steps towards merging these until the elements marked out in the TODO are done and the PR this is based on is merged, but I expect it to take a while to effectively review all these changes.

--- BastiaanOlij:
Some initial testing, after fixing an issue in @RandomShaper PR, this is working on both desktop VR (tested with an Valve Index headset) and on Quest (tested on Quest 3). I have more testing to do.

This was done with the mobile renderer, there weren't any obvious performance improvements but I wasn't expecting any as the mobile renderer already has a minimum of passes, there isn't much for the graph to optimise.

I did notice when testing on the Quest 3 that MSAA broke, as far as I can tell it looks like it's resolving MSAA before it has finished rendering, so there is an issue in barriers. I did not test this with just @RandomShaper PR, so not 100% sure if this is introduced by the acyclic graph or if we're missing something in the new barrier code.

--- DarioSamo:
> I did notice when testing on the Quest 3 that MSAA broke, as far as I can tell it looks like it's resolving MSAA before it has finished rendering, so there is an issue in barriers. I did not test this with just @RandomShaper PR, so not 100% sure if this is introduced by the acyclic graph or if we're missing something in the new barrier code.

I've double checked with 3D platformer on these combinations and MSAA seems to be working. Also with the latest version of the Vulkan validation and synchronization layers.

- Forward+ and NVIDIA
- Forward+ and AMD
- Mobile and NVIDIA
- Mobile and AMD

As far as I can tell, the mobile renderer does not make use of the manual command to resolve MSAA textures and instead delegates the responsibility to the render pass.

It seeems we're missing some details as to what scenario triggers it, if it's the mobile hardware or some effect your test project might have enabled that causes it.

--- Calinou:
Tested locally, here's a benchmark using https://github.com/Calinou/godot-reflection/tree/add-benchmark (`-- --benchmark` CLI argument):

## Benchmark

**OS:** Windows 10 22H2
**CPU:** Intel Core i7-6700K @ 4.4 GHz
**RAM:** 2×16 GB DDR4-3000 C15
**GPU:** AMD Radeon RX 6900 XT
**Resolution:** 2560×1440 fullscreen

#### `rd_common` cc8843db4


|          | Average             | 1% low              | 0.1% low|
|---------:|---------------------|---------------------|------------------------|
|Frametime | 267 FPS (3.73 mspf) | 194 FPS (5.15 mspf) | 163 FPS (6.10 mspf)|
|CPU Time | 2036 FPS (0.49 mspf) | 1485 FPS (0.67 mspf) | 1256 FPS (0.80 mspf)|
|GPU Time | 283 FPS (3.53 mspf) | 202 FPS (4.93 mspf) | 171 FPS (5.82 mspf)|

#### `rd_common_render_graph` 2c1954dc1

|           | Average             | 1% low              | 0.1% low|
|---------:|---------------------|---------------------|------------------------|
|Frametime | 270 FPS (3.70 mspf) | 194 FPS (5.15 mspf) | 166 FPS (6.00 mspf)|
|CPU Time | 3368 FPS (0.30 mspf) | 2747 FPS (0.36 mspf) | 2283 FPS (0.44 mspf)|
|GPU Time | 289 FPS (3.46 mspf) | 201 FPS (4.97 mspf) | 172 FPS (5.79 mspf)|

___

**OS:** Fedora 39
**CPU:** Intel Core i7-13900K
**RAM:** 2×32 GB DDR4-5800 C30
**GPU:** NVIDIA GeForce RTX 4090

**Resolution:** 3840×2160 fullscreen

#### `rd_common` cc8843db4

|          | Average             | 1% low              | 0.1% low|
|---------:|---------------------|---------------------|------------------------|
|Frametime | 248 FPS (4.02 mspf) | 194 FPS (5.15 mspf) | 135 FPS (7.36 mspf)|
|CPU Time | 5226 FPS (0.19 mspf) | 3460 FPS (0.29 mspf) | 2801 FPS (0.36 mspf)|
|GPU Time | 258 FPS (3.87 mspf) | 201 FPS (4.95 mspf) | 138 FPS (7.24 mspf)|

#### `rd_common_render_graph` 2c1954dc1

|          | Average             | 1% low              | 0.1% low|
|---------:|---------------------|---------------------|------------------------|
|Frametime | 256 FPS (3.90 mspf) | 203 FPS (4.90 mspf) | 135 FPS (7.37 mspf)|
|CPU Time | 7045 FPS (0.14 mspf) | 5464 FPS (0.18 mspf) | 4608 FPS (0.22 mspf)|
|GPU Time | 266 FPS (3.75 mspf) | 210 FPS (4.76 mspf) | 139 FPS (7.15 mspf)|

**Resolution:** 1280×720 window

#### `rd_common` cc8843db4

|          | Average             | 1% low              | 0.1% low|
|---------:|---------------------|---------------------|------------------------|
|Frametime | 939 FPS (1.06 mspf) | 656 FPS (1.52 mspf) | 459 FPS (2.18 mspf)|
| CPU Time | 6501 FPS (0.15 mspf) | 4784 FPS (0.21 mspf) | 3636 FPS (0.28 mspf)|
| GPU Time | 992 FPS (1.01 mspf) | 752 FPS (1.33 mspf) | 520 FPS (1.92 mspf)|

#### `rd_common_render_graph` 2c1954dc1

|          | Average             | 1% low              | 0.1% low|
|---------:|---------------------|---------------------|------------------------|
|Frametime | 1127 FPS (0.89 mspf) | 879 FPS (1.14 mspf) | 580 FPS (1.72 mspf)|
| CPU Time | 8705 FPS (0.11 mspf) | 7194 FPS (0.14 mspf) | 5154 FPS (0.19 mspf)|
| GPU Time | 1186 FPS (0.84 mspf) | 1005 FPS (1.00 mspf) | 621 FPS (1.61 mspf)|

Also, https://github.com/godotengine/tps-demo's 3D rendering is broken with errors spammed in the console. Only glow renders and nothing else:

```
ERROR: All the shader bindings for the given set must be covered by the uniforms provided. Binding (5), set (1) was not provided.
   at: uniform_set_create (./servers/rendering/rendering_device.cpp:2402)
ERROR: Condition "rid.is_null()" is true. Returning: rid
   at: _allocate_from_uniforms (./servers/rendering/renderer_rd/uniform_set_cache_rd.h:129)
ERROR: Parameter "uniform_set" is null.
   at: compute_list_bind_uniform_set (./servers/rendering/rendering_device.cpp:3747)
ERROR: Uniforms were never supplied for set (1) at the time of drawing, which are required by the pipeline
   at: compute_list_dispatch (./servers/rendering/rendering_device.cpp:3844)
```

--- DarioSamo:
@Calinou Were you perhaps testing the demo with FSR2? The binding (5) had to be removed from the third party shader, but it seems scons doesn't pick up the change when you test between branches. Getting rid of the `fsr2*.gen.h` files usually fixes it for me.

Seems from the numbers we can draw the conclusion that the benefits aren't as visible if the resolution is very high due to synchronization being less relevant as the rendering takes a bigger chunk of the frame time.

It's worth noting the CPU stat will be misleading though, there's no way it can actually reduce the time, but that's because it defers it until the end of the frame. I believe the current profiler only picks the CPU time inside of the viewport itself. The CPU time has been measurably bigger for me although it'll go down with the immutable change.

--- Calinou:
> Were you perhaps testing the demo with FSR2? 

The TPS demo uses FSR2 by default now, so yes.

>  I believe the current profiler only picks the CPU time inside of the viewport itself. 

Indeed, I measure it by adding the CPU time taken by the viewport + the frame setup time (which is the same across all viewports).

--- DarioSamo:
 > The TPS demo uses FSR2 by default now, so yes.

I believe it should work fine if you build it after deleting those files then and letting them regenerate. This seems like an issue with the Scons configuration in general to detect that the third party dependency has changed when switching branches.

Basically there was an unneeded shader bind that caused a validation error (using an image as both sampling and storage in the same uniform set), but the shader didn't actually use it so the macro just needed to be removed.

--- clayjohn:
I tested this on two devices quite roughly so far. I tested using a modified TPS demo that includes more skeletons, more particles, and decals

In editor I tested on my intel integrated graphics (Intel® Core™ i7-1165G7; Xe graphics) and saw a GPU frame time drop from 23.5 mspf to 19 mspf

I tested on a Pixel 7 using the one-click deploy and saw no change in frame time. Both ran at 26-27 FPS
Testing on the Pixel 7 with release builds and I get a slight change:
This PR: 30-33 FPS
Master: 27-31 FPS
Its worth noting that Master has some issues during loading where artifacts flash on the screen that are resolved by this PR. 

I have a feeling the immutable resource optimizations are going to have a greater impact on mobile than they do on desktop

--- DarioSamo:
As per @reduz's suggestion, any meshes that don't specify `ARRAY_FLAG_USE_DYNAMIC_UPDATE` will be considered immutable if they're not used as storage. Therefore, their vertex buffers and index buffers do not create trackers anymore, greatly reducing CPU overhead.

We're still not quite on par with `master` on this regard, as I'm still getting CPU-bottlenecked in this draw-call saturated scene I'm testing out, but it's gotten much closer now.

--- DarioSamo:
After discussing a bit with @clayjohn an idea came up to automatically make resources mutable only when RD requests it, with the implication the graph has to insert a full synchronization whenever that happens.

I added this change and haven't detected anything breaking so far along with a great reduction of the CPU overhead on scenes with lots of resources being bound. This would effectively nullify the need of @reduz's immutable PR (#85830) (as far as the graph is concerned) so let's see how it works without that.

--- Calinou:
I still have the issue with only glow appearing in the TPS demo as of 381f30381 (on Windows + NVIDIA).

```
ERROR: All the shader bindings for the given set must be covered by the uniforms provided. Binding (5), set (1) was not provided.
   at: (servers\rendering\rendering_device.cpp:2474)
ERROR: Condition "rid.is_null()" is true. Returning: rid
   at: UniformSetCacheRD::_allocate_from_uniforms (.\servers/rendering/renderer_rd/uniform_set_cache_rd.h:129)
ERROR: Parameter "uniform_set" is null.
   at: RenderingDevice::compute_list_bind_uniform_set (servers\rendering\rendering_device.cpp:3878)
ERROR: Uniforms were never supplied for set (1) at the time of drawing, which are required by the pipeline
   at: (servers\rendering\rendering_device.cpp:3975)
```

--- DarioSamo:
@Calinou Have you tried clearing the header files I mentioned in my previous comment before trying to build the branch? I don't think your issue will happen from a clean build, as it's failing due to Scons being unable to detect the third party file has changed.

I just double checked and the TPS demo works fine for me, so I think it's just that. I'm not sure how we can fix it yet.

--- Calinou:
> @Calinou Have you tried clearing the header files I mentioned in my previous comment before trying to build the branch? I don't think your issue will happen from a clean build, as it's failing due to Scons being unable to detect the third party file has changed.

I just did a clean build on Linux and it worked, apologies for that. The TPS demo renders correctly now, although I can't spot any performance increase in both 1280×720 and 4K on a RTX 4090.

--- DarioSamo:
 > I just did a clean build on Linux and it worked, apologies for that.

No worries, I should have fixed that anyway. I just pushed a fix for the dependencies.

For what it's worth the performance improvement from the latest change I made is only the CPU cost, if the scene is GPU-bound it won't make any difference.

--- DarioSamo:
I've rebased the branch on top of @RandomShaper's latest changes, although D3D12 remains unverified and not working until he finishes that up. There's one new command I want to review with him first before adding it to the graph as it's D3D12-only for now and a couple other things.

There should hopefully be no regressions functionality or performance wise from this but it's probably worth a check again.

--- DarioSamo:
I've rebased on top of RDD once more, this time enabling D3D12 support and adding the missing commands. It's worth noting the graph won't get that much benefit out of assigning the barriers until the D3D12 RDD implements enhanced barriers, so it'll pretty much skip on doing that until they're actually implemented.

However, there seems to be an issue with the command reordering the graph does, which causes a validation error during some operations and what the root signature expects. It doesn't seem to cause any particular visual errors but I'll discuss with @RandomShaper what the underlying cause of the error is.

--- DarioSamo:
I've rebased on top of `master` and confirmed mostly everything is working.

I've re-ran the tests on a lot of scenarios and they all seem to be working fine. However, I must point out I've noticed the impact of the CPU overhead caused by the command recording in an internal demo scene that has a ton of draw calls (around 25K+). While when starting this we theorized the impact of the CPU overhead would be caused by the graph command dependency detection and reordering, it seems the heavier impact is on scenes with a ton of draw calls with different vertex buffers. The actual part of the graph is probably the least expensive of the frame CPU-wise. I've been unable to make any significant optimizations about this as it's part of the design to serialize this into a separate buffer and then translate it to the driver calls. Most of the significant cost is there when the draw lists are really extensive.

Secondary command buffers can help offset it a lot because it allows to overlap the recording of the graph with the rest of the operations and get ahead of the final step by recording with the driver the draw lists that are already finished. This actually compensates pretty significantly the overhead I've noticed in this demo scene, but as long as secondary command buffers show the weird issue I explained in the TODO I'm not confident in enabling them by default.

If we're going ahead with merging this, we should be aware the CPU cost is not free, but the parts that should be optimized to fix it are beyond the scope of what RD can do.

--- Saul2022:
I think got some weird performance boost even on a scene without animations or particles active, where  the gpu has slightly more performance and the cu cost seem´s to be even lower than the 4.2 version. ( also the  weird texture in the 4.3 version prob  just the terrain addon bug, as leaf textures don´t have that issue).Specs are amd radeon vega 3 with 8GB of ram lenovo ideapad 3. scaling was at 0.7 in both with fsr 1.

![editor_screenshot_2023-12-21T161937](https://github.com/godotengine/godot/assets/97898580/1a73b135-5087-499d-87f2-825689b61b85)
![editor_screenshot_2023-12-21T162008](https://github.com/godotengine/godot/assets/97898580/087bcb0a-9fa1-4f4f-b8a3-8fda824420f5)


--- DarioSamo:
> I think got some weird performance boost even on a scene without animations or particles active, where the gpu has slightly more performance and the cu cost seem´s to be even lower than the 4.2 version. ( also the weird texture in the 4.3 version prob just the terrain addon bug, as leaf textures don´t have that issue).Specs are amd radeon vega 3 with 8GB of ram lenovo ideapad 3. scaling was at 0.7 in both with fsr 1.

The viewport does not reliably measure the entire CPU time, as the cost of the command list recording is now deferred to right before command lists are submitted, which happens outside of the range the viewport profiles. Therefore you'll likely see the viewport CPU time go lower in about all scenarios.

The more reliable benchmark is indeed just no V-Sync FPS in any project and measure the in-game FPS. In situations where the CPU limitation matters it'll show up, but it's unlikely it will in simpler projects.

--- AThousandShips:
You'd need to compare with a custom build to get fair results, the official downloads are optimized (which would yield even better results) so I'd suggest comparing with the base of this branch to get the best comparison (also the artifacts of the build are stripped down so not guaranteed to be representative, to do a proper comparison you should build both yourself)

--- Saul2022:
> You'd need to compare with a custom build to get fair results,   


Alright , thank you starting compiling though it takes hours(just 2 thread in cpu) ,also it would be better to conpare with a more complex scene geometry wise no? chatgpt said it

--- atirutw:
> also it would be better to conpare with a more complex scene geometry wise no? chatgpt said it

Kinda. It's more nuanced than that.

--- clayjohn:
Results so far:

### 11th Gen Intel® Core™ i7-1165G7 @ 2.80GHz × 8

#### Modified TPS demo (includes more particles, decals, skeletons + uses mobile renderer):
- 32 mspf - > 30 mspf

#### Complex scene ([Legend of the Nuku Warriors](https://youtu.be/9kcjFJJxO6I?si=jXtcfo_nK6LXwwlC))
Uses GI, heavy shaders, a lot of meshes, a lot of textures.

No apparent graphical artifacts, no measurable change in performance.

#### Particles:
The [particles benchmark](https://github.com/Geometror/godot-tests-and-benchmarks) is very successful on this device. It shows a slight reduction in particles cost in all cases, but there is a notable reduction in frame time for cases with a high number of particle systems and low numbers of particles.

<details>
  <summary>Particle benchmark details</summary>

```
Before
-------------------------------------------------------------
🟩 Results (particle systems: 320, particles per system: 8):
CPU Particles : 7.2872 mspf
GPU Particles (unique process materials 1) : 4.1980 mspf
GPU Particles (unique process materials 10) : 4.2184 mspf
GPU Particles (unique process materials 320) : 4.2614 mspf

🟩 Results (particle systems: 320, particles per system: 16):
CPU Particles : 10.8680 mspf
GPU Particles (unique process materials 1) : 4.4340 mspf
GPU Particles (unique process materials 10) : 4.4386 mspf
GPU Particles (unique process materials 320) : 4.4426 mspf

🟩 Results (particle systems: 320, particles per system: 32):
CPU Particles : 17.6263 mspf
GPU Particles (unique process materials 1) : 4.7181 mspf
GPU Particles (unique process materials 10) : 4.7421 mspf
GPU Particles (unique process materials 320) : 4.7369 mspf

🟩 Results (particle systems: 80, particles per system: 128):
CPU Particles : 15.6845 mspf
GPU Particles (unique process materials 1) : 2.5515 mspf
GPU Particles (unique process materials 10) : 2.5591 mspf
GPU Particles (unique process materials 80) : 2.5640 mspf

🟩 Results (particle systems: 20, particles per system: 512):
CPU Particles : 15.3872 mspf
GPU Particles (unique process materials 1) : 2.1072 mspf
GPU Particles (unique process materials 10) : 2.1110 mspf
GPU Particles (unique process materials 20) : 2.0998 mspf

-------------------------------------------------------------

After
-------------------------------------------------------------
🟩 Results (particle systems: 320, particles per system: 8):
CPU Particles : 7.2954 mspf
GPU Particles (unique process materials 1) : 3.5932 mspf
GPU Particles (unique process materials 10) : 3.6328 mspf
GPU Particles (unique process materials 320) : 3.6578 mspf

🟩 Results (particle systems: 320, particles per system: 16):
CPU Particles : 11.0647 mspf
GPU Particles (unique process materials 1) : 3.6760 mspf
GPU Particles (unique process materials 10) : 3.7013 mspf
GPU Particles (unique process materials 320) : 3.7227 mspf

🟩 Results (particle systems: 320, particles per system: 32):
CPU Particles : 17.8069 mspf
GPU Particles (unique process materials 1) : 3.7905 mspf
GPU Particles (unique process materials 10) : 3.7272 mspf
GPU Particles (unique process materials 320) : 3.7602 mspf

🟩 Results (particle systems: 80, particles per system: 128):
CPU Particles : 16.0834 mspf
GPU Particles (unique process materials 1) : 2.1293 mspf
GPU Particles (unique process materials 10) : 2.1295 mspf
GPU Particles (unique process materials 80) : 2.1305 mspf

🟩 Results (particle systems: 20, particles per system: 512):
CPU Particles : 15.7018 mspf
GPU Particles (unique process materials 1) : 2.0117 mspf
GPU Particles (unique process materials 10) : 2.0067 mspf
GPU Particles (unique process materials 20) : 2.0158 mspf

-------------------------------------------------------------
```
</details>

### Pixel 7

#### Modified TPS demo (includes more particles, decals, skeletons + uses mobile renderer):
- 37 mspf - > 34 mspf

#### Particles
Particles benchmark was very successful. All the overhead from using a high number of particle systems was reduced. And (like the Desktop example), there is no longer a performance penalty for having a high number of particle systems. This finding is likely only true on devices that actually support compute shaders (relatively new devices).
<details>
  <summary>Particle benchmark details</summary>

```
Before
-------------------------------------------------------------
🟩 Results (particle systems: 320, particles per system: 8):
CPU Particles : 11.2111 mspf
GPU Particles (unique process materials 1) : 36.1811 mspf
GPU Particles (unique process materials 10) : 36.1518 mspf
GPU Particles (unique process materials 320) : 36.2588 mspf

🟩 Results (particle systems: 320, particles per system: 16):
CPU Particles : 11.2129 mspf
GPU Particles (unique process materials 1) : 39.9706 mspf
GPU Particles (unique process materials 10) : 40.0203 mspf
GPU Particles (unique process materials 320) : 40.2861 mspf

🟩 Results (particle systems: 320, particles per system: 32):
CPU Particles : 11.2259 mspf
GPU Particles (unique process materials 1) : 46.3663 mspf
GPU Particles (unique process materials 10) : 46.2579 mspf
GPU Particles (unique process materials 320) : 46.4068 mspf

🟩 Results (particle systems: 80, particles per system: 128):
CPU Particles : 11.1662 mspf
GPU Particles (unique process materials 1) : 11.1507 mspf
GPU Particles (unique process materials 10) : 11.1487 mspf
GPU Particles (unique process materials 80) : 11.1662 mspf

🟩 Results (particle systems: 20, particles per system: 512):
CPU Particles : 11.1551 mspf
GPU Particles (unique process materials 1) : 11.1402 mspf
GPU Particles (unique process materials 10) : 11.1423 mspf
GPU Particles (unique process materials 20) : 11.1507 mspf

-------------------------------------------------------------

After
-------------------------------------------------------------
🟩 Results (particle systems: 320, particles per system: 8):
CPU Particles : 11.2118 mspf
GPU Particles (unique process materials 1) : 11.3576 mspf
GPU Particles (unique process materials 10) : 11.3379 mspf
GPU Particles (unique process materials 320) : 11.4896 mspf

🟩 Results (particle systems: 320, particles per system: 16):
CPU Particles : 11.2022 mspf
GPU Particles (unique process materials 1) : 11.6893 mspf
GPU Particles (unique process materials 10) : 11.7781 mspf
GPU Particles (unique process materials 320) : 11.7556 mspf

🟩 Results (particle systems: 320, particles per system: 32):
CPU Particles : 11.2164 mspf
GPU Particles (unique process materials 1) : 12.0266 mspf
GPU Particles (unique process materials 10) : 12.0397 mspf
GPU Particles (unique process materials 320) : 12.1320 mspf

🟩 Results (particle systems: 80, particles per system: 128):
CPU Particles : 11.1667 mspf
GPU Particles (unique process materials 1) : 11.1572 mspf
GPU Particles (unique process materials 10) : 11.1527 mspf
GPU Particles (unique process materials 80) : 11.1819 mspf

🟩 Results (particle systems: 20, particles per system: 512):
CPU Particles : 11.1611 mspf
GPU Particles (unique process materials 1) : 11.1527 mspf
GPU Particles (unique process materials 10) : 11.1527 mspf
GPU Particles (unique process materials 20) : 11.1548 mspf

-------------------------------------------------------------
```
</details>

### Pixel 4

#### Modified TPS demo (includes more particles, decals, skeletons + uses mobile renderer):
- No measurable change. This device really struggles with this scene and the bottleneck is likely not impacted by this PR
- No graphical artifacts or any other detectable issues


#### Particles
There is a similar improvement to Desktop. This likely indicates that compute shaders are run on the CPU for this device and the expense comes from the round trip from GPU -> CPU -> GPU. The slight improvement makes sense, as we are still removing barriers and allowing the work to overlap, but the gains from overlapping work on the CPU are much smaller than the gains from overlapping work on the GPU
<details>
  <summary>Particle benchmark details</summary>

```
Before
-------------------------------------------------------------
🟩 Results (particle systems: 320, particles per system: 8):
CPU Particles : 16.7495 mspf
GPU Particles (unique process materials 1) : 23.3405 mspf
GPU Particles (unique process materials 10) : 22.6339 mspf
GPU Particles (unique process materials 320) : 22.3498 mspf

🟩 Results (particle systems: 320, particles per system: 16):
CPU Particles : 17.0838 mspf
GPU Particles (unique process materials 1) : 28.6934 mspf
GPU Particles (unique process materials 10) : 28.8401 mspf
GPU Particles (unique process materials 320) : 28.4595 mspf

🟩 Results (particle systems: 320, particles per system: 32):
CPU Particles : 26.5548 mspf
GPU Particles (unique process materials 1) : 40.8826 mspf
GPU Particles (unique process materials 10) : 42.3289 mspf
GPU Particles (unique process materials 320) : 42.1029 mspf

🟩 Results (particle systems: 80, particles per system: 128):
CPU Particles : 24.8579 mspf
GPU Particles (unique process materials 1) : 26.3309 mspf
GPU Particles (unique process materials 10) : 25.9565 mspf
GPU Particles (unique process materials 80) : 26.1425 mspf

🟩 Results (particle systems: 20, particles per system: 512):
CPU Particles : 24.4292 mspf
GPU Particles (unique process materials 1) : 24.1131 mspf
GPU Particles (unique process materials 10) : 24.1181 mspf
GPU Particles (unique process materials 20) : 24.1165 mspf

-------------------------------------------------------------



After
-------------------------------------------------------------
🟩 Results (particle systems: 320, particles per system: 8):
CPU Particles : 16.7964 mspf
GPU Particles (unique process materials 1) : 20.6662 mspf
GPU Particles (unique process materials 10) : 21.2597 mspf
GPU Particles (unique process materials 320) : 20.9503 mspf

🟩 Results (particle systems: 320, particles per system: 16):
CPU Particles : 16.9076 mspf
GPU Particles (unique process materials 1) : 25.0367 mspf
GPU Particles (unique process materials 10) : 24.8971 mspf
GPU Particles (unique process materials 320) : 24.9487 mspf

🟩 Results (particle systems: 320, particles per system: 32):
CPU Particles : 25.2311 mspf
GPU Particles (unique process materials 1) : 36.2112 mspf
GPU Particles (unique process materials 10) : 35.2176 mspf
GPU Particles (unique process materials 320) : 37.9688 mspf

🟩 Results (particle systems: 80, particles per system: 128):
CPU Particles : 23.9004 mspf
GPU Particles (unique process materials 1) : 25.8008 mspf
GPU Particles (unique process materials 10) : 25.7384 mspf
GPU Particles (unique process materials 80) : 25.4694 mspf

🟩 Results (particle systems: 20, particles per system: 512):
CPU Particles : 24.2083 mspf
GPU Particles (unique process materials 1) : 23.8697 mspf
GPU Particles (unique process materials 10) : 23.8262 mspf
GPU Particles (unique process materials 20) : 23.8831 mspf

-------------------------------------------------------------
```
</details>

--- RandomShaper:
> However, there seems to be an issue with the command reordering the graph does, which causes a validation error during some operations and what the root signature expects. It doesn't seem to cause any particular visual errors but I'll discuss with @RandomShaper what the underlying cause of the error is.

#86522 may be of help.

--- DarioSamo:
> #86522 may be of help.

Can confirm it doesn't change the situation.

--- DarioSamo:
> However, there seems to be an issue with the command reordering the graph does, which causes a validation error during some operations and what the root signature expects. It doesn't seem to cause any particular visual errors but I'll discuss with @RandomShaper what the underlying cause of the error is.

I've been unable to determine the real cause of this so far but my investigation leads me to believe the error is a false positive. I think we're safe to merge this until I get more information from a more knowledgeable party on the nature of the error, as it doesn't seem to cause any issues so far.

I've rebased on top of the latest master.

--- DarioSamo:
Applied the style fixes as well as removed some dead code.

--- akien-mga:
Tested on the [GDQuest TPS demo](https://github.com/gdquest-demos/godot-4-3d-third-person-controller), it glitches and flickers a lot:

![image](https://github.com/godotengine/godot/assets/4701338/3fc58149-43f2-46c9-88e3-9341bdd270e1)
![image](https://github.com/godotengine/godot/assets/4701338/18c684df-bc58-4554-950a-240b7079e093)

Comparing with current `master`:

![image](https://github.com/godotengine/godot/assets/4701338/bce7024a-8a19-4995-bec6-5735cc30b7ac)

<details>

<summary>System specs</summary>

```
System:
  Host: cauldron Kernel: 6.5.13-desktop-6.mga9 arch: x86_64 bits: 64
    Desktop: KDE Plasma v: 5.27.5 Distro: Mageia 9
CPU:
  Info: quad core model: Intel Core i7-8705G bits: 64 type: MT MCP cache:
    L2: 1024 KiB
  Speed (MHz): avg: 3099 min/max: 800/4100 cores: 1: 3100 2: 3100 3: 3101
    4: 3100 5: 3098 6: 3100 7: 3100 8: 3100
Graphics:
  Device-1: Intel HD Graphics 630 driver: i915 v: kernel
  Device-2: AMD Polaris 22 XL [Radeon RX Vega M GL] driver: amdgpu v: kernel
  Device-3: Cheng Uei Precision Industry (Foxlink) HP Wide Vision FHD Camera
    type: USB driver: uvcvideo
  Display: x11 server: X.org v: 1.21.1.8 with: Xwayland v: 22.1.9 driver: X:
    loaded: intel,v4l dri: i965 gpu: i915 resolution: 2048x1152~60Hz
  API: OpenGL v: 4.6 Mesa 23.1.9 renderer: Mesa Intel HD Graphics 630 (KBL
    GT2)
```

Running with the AMD Radeon RX Vega M dGPU.

</details>

--- DarioSamo:
@akien-mga I tested that project just now in both the RTX 3090ti and the AMD iGPU of the 7950x with both GPU validation and synchronization layers and got no errors about it (on Windows, but I doubt it's related unless the driver is at fault). Can you reproduce this consistently from a clean build?

--- akien-mga:
I made a clean build of e1a29bd, the glitch is consistently reproducible for me with AMD Radeon RX Vega M. I made sure to remove the `res://.godot` folder, `~/.local/share/godot/shader_cache`, and `~/.cache/godot` to check that it wasn't a caching issue. I don't see any useful output from `--gpu-validation --verbose`.

On the other hand, it's not reproducible with Intel HD 630 on the same laptop. Both using Mesa 23.1.9.

~I'll test on another AMD laptop.~

*Edit:* As discussed on chat, setting either `RENDER_GRAPH_REORDER` to 0 or `RENDER_GRAPH_FULL_BARRIERS` to 1 fixes the issue for me, which Dario identifies as a synchronization issue.

--- DarioSamo:
Some further investigation on the scene itself indicates the player character or something related might be at fault, but a RenderDoc capture doesn't show anything strange about the synchronization: it is in fact pretty much correct as far as the synchronization between the compute skinning step and the depth pre-pass goes (using a single memory barrier).

--- DarioSamo:
In a weird twist of fate, it seems enabling buffer barriers also fixes the issue while retaining the ability to both reorder the graph and not have to rely on full barriers to synchronize on the AMD Radeon RX Vega M.

Since the main suspect is the compute skinning right now, it might be a good idea to try to exaggerate the issue on the project by creating multiple skinned characters so if any race condition exists, it'll be more likely to show up.

--- DarioSamo:
The conclusions after talking with @akien-mga seem to be so far:

1. The issue does not happen if buffer barriers are used instead, no matter how much the system is pushed to duplicate as many animated characters as possible. It happens instantly if buffer barriers are re-enabled.
2. The issue does not happen in the Windows 10 artifact from the PR on the same hardware with regular memory barriers instead.

We should probably discuss how to approach this, as it could be a hint of something being wrong in the driver/system combination itself. Reviewing the RenderDoc capture has not revealed anything apparent nor does the validation or synchronization layer show any errors about it. It might be possible to build a standalone sample using Vulkan that replicates the issue if we want to dedicate time to that.

Alternatively, we can enable buffer barriers by default at the cost of some performance and trusting that IHVs implement them correctly (or at least basically translate them to global barriers internally).

--- DarioSamo:
Well this is a bad discovery to make at the last minute, but it turns out that at some point, my Vulkan Validation misconfigured itself and actually turned off my synchronization checking, and now I get some synchronization errors that @akien-mga was reporting (not the error that was reported on the scene however, the visuals themselves are still fine). I realized this when I went to test another project and was wondering why I was not getting synchronization errors in a more obvious scenario.

I'd suggest avoiding to merge this until these synchronization errors are addressed, as there's quite a lot more than I thought there were due to the Validation layer turning itself off at some point during development.

EDIT: Upon further testing I can confirm when forcing the full barrier access bits most of the errors are gone at least, so the rendering graph logic itself seems fine, it just needs some further tweaking for correctness and analyzing what's missing from these cases.

--- DarioSamo:
I was able to solve most of the synchronization errors, although one of the solutions will probably remain a bit temporary until a more proper solution is figured out, but it's not exactly a pressing case as it involves an edge case with slices transitions (mostly due to how reflection probes behave).

There's another synchronization error in the TPS project, but it seems actually unrelated to the graph and it has more to do with the texture upload in particular of that project. It's worth checking if that error shows up as well in `master` at the moment or if https://github.com/godotengine/godot/pull/86855 might be related.

--- Ansraer:
Oh thank god. I am building a PR on top of the RenderGraph and couldn't figure out why the layers were screaming at me when I hadn't even launched my new compute shader yet.

--- DarioSamo:
> Oh thank god. I am building a PR on top of the RenderGraph and couldn't figure out why the layers were screaming at me when I hadn't even launched my new compute shader yet.

Were you using only validation or synchronization? I never saw errors with regular validation so far, but don't hesitate to report anything that might've been missed.

--- akien-mga:
I retested the latest version of this PR (d7ea8b7). I confirm that:
- With buffer barriers (current PR), the skinning glitch I reproduce on Mesa radv is no longer present.
- If I disable buffer barriers, the glitch comes back.

--- DarioSamo:
@akien-mga tested a standalone Vulkan sample that I created but we were unable to reproduce the glitch he's getting when using only memory barriers instead of buffer barriers. It seems it'll be much harder to trace what exactly is failing here and what part of the operations are corrupting it.

--- akien-mga:
Thanks and congrats, this is an amazing change! :tada: :1st_place_medal: 


# PR 112506 [MERGED] — CommandQueueMT: Reduce contention + Fix race conditions
AUTHOR: RandomShaper

## BODY
See #112452 for an explanation of why this would be beneficial.

TL;DR Keeping the lock held over the command queue of the rendering server in separate thread mode is not needed because there's a single thread dealing with such server, Therefore, the lock is only needed for thread safety of the command queue itself, which means the lock can be released while commands are run, allowing other threads to add commands without waiting.

Not tested at all due to lack of time...

**UPDATE:** I've marked this PR as cherry-pickable into some releases, but probably the only commit that should be cherry-picked is the first one (_CommandQueueMT: Fix race conditions_), which fixes a clear bug. The rest of the PR is a performance improvement, and as such it's better scheduled only for the current dev branch.

## COMMENTS
--- brycehutchings:
I did some basic testing of this fix using the Sponza scene (https://github.com/Calinou/godot-sponza). I confirmed it fixes the performance problem so that the performance loading a very complex glTF in a background thread takes the same time regardless of if using the Separate or Safe thread model. I also compared it to the performance without the fix for loading with Safe thread model and it was comparable, so I didn't see a degradation due to the memcpy.

--- RandomShaper:
@brycehutchings Thanks a lot for testing and reviewing this.

--- RandomShaper:
Rebased.

--- dsnopek:
I noticed the issue with the lock being held while the RenderingServer is flushing the queue (and stalling everything that's queuing stuff for the next frame) while looking at Perfetto traces on Samsung Galaxy XR.

This PR seems to solve that problem entirely!

**Here's a trace from `master` running [my fork of the GDQuest TPS demo](https://github.com/dsnopek/gdquest-tps-demo/tree/standalone-vr-slush-drs-benchmarking):**

<img width="1277" height="351" alt="Selection_396" src="https://github.com/user-attachments/assets/e2039367-5f32-45e5-bc96-c5df37e79b04" />

The `set_render_display_info` is the first thing on this frame that is attempting to queue a `Callable` for the rendering server, and it ends up stalled there until the render thread finishes rendering the previous frame. You can see all the process stuff waiting until the end.

_(NOTE: this won't show up in traces of this project on Meta Quest 3, because Meta's runtime uses `xrWaitFrame()` to delay running process until close to the end of the frame anyway to improve input latency. However, it's still possible to trigger the issue there too, just not in this project and not as drastically.)_

**And here is a trace from this PR:**

<img width="1223" height="325" alt="Selection_397" src="https://github.com/user-attachments/assets/3b9dc900-e659-46ae-aa8d-e282c1ef98b5" />

Notice that the process stuff happens super early now and overlaps the rendering, and it's only the `RenderingServer::sync()` that stalls until the rendering server is done, which is exactly what we would expect.

_(NOTE: this trace is actually worse for input latency, but I think that's really a problem with `xrWaitFrame()` on Samsung Galaxy XR. Inadvertent lock contention on Godot's `RenderingServer` shouldn't be used as the solution for that :-))_

--- Repiteo:
Thanks!

--- blueskythlikesclouds:
I've been having random crashes during resource loading and I managed to pinpoint it to this PR. TPS Demo can randomly crash during the loading screen due to heap corruptions.


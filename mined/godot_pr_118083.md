# PR 118083 [MERGED] — Add HDR output support to Vulkan on macOS.
AUTHOR: allenwp

## BODY
### What problem(s) does this PR solve?

- HDR output does not function with the Vulkan rendering device driver on macOS.
- Users targeting macOS with HDR support must check project settings to ensure they are not using the Vulkan driver. This complicates the debugging experience for users.
- Documentation for HDR output is a tiny bit more complicated by needing to note that Vulkan does not support HDR output on macOS.

### What is the rationale for the approach used in this PR?

When HDR output support was added to Apple platforms, the PR was pretty big and there was a lot to test. At the time, we [decided that Vulkan support would be better suited for a followup PR](https://github.com/godotengine/godot/pull/106814#issuecomment-3886589015). This is that followup PR.

**iOS**

I tested iOS vulkan support on my iPhone 13 Pro and it doesn't work well. If I switch from an HDR app to my vulkan Godot app, it appears like HDR output works well for a moment, and then snaps down to 1.2 max linear value. After a few moments, it will drop to a max linear value of 1.0 and stay there. Strange behaviour. Smells like an iOS vulkan driver bug to me. Probably best to just leave iOS not supporting HDR output on Vulkan until someone wants to figure out what's going on.

(Note for those who know the history: [I was wrong with my initial guess about why Vulkan wasn't working](https://github.com/godotengine/godot/pull/106814#issuecomment-3886550928). Turns out linear luminance scale needs to be reference luminance on Vulkan as well. My apologies!)

### Was generative AI (LLM AI) used to create a portion of this PR?

No.

### Are there any parts of this PR that you are uncertain of or require special attention from reviewers?

- I believe that it would be better to merge this sooner rather than later, specifically before Godot 4.7 goes into feature freeze/beta. This way we will get maximum testing of Vulkan HDR output on macOS during the beta period. In the future, it may be a lot harder to get real-world testing of this feature. If this turns out to be broken, we can always roll back support before 4.7 goes stable.

I've tested on my Macbook Pro with an external display connected and everything seems to be working great.

## COMMENTS
--- Calinou:
> If I switch from an HDR app to my vulkan Godot app, it appears like HDR output works well for a moment, and then snaps down to 1.2 max linear value. After a few moments, it will drop to a max linear value of 1.0 and stay there. Strange behaviour. Smells like an iOS vulkan driver bug to me. 

This could be the result of thermal throttling, as high screen brightness requires a low enough device temperature (also on Android). Automatic screen brightness based on the ambient light sensor can also cause the output max linear value to change over time, so make sure to disable it during testing.

--- allenwp:
Rebased to resolve trivial conflict.

I also added DarkKilauea and stuartcarnie as co-authors to this PR because DarkKilauea did most of the work on Vulkan and stuartcarnie did most of the work on macOS. All I did was remove a `#ifdef` and test that it worked correctly.

--- Repiteo:
Thanks!

--- ArchercatNEO:
@allenwp @stuartcarnie previously we concluded that the Macos display server didn't need to check whether enabling HDR for metal worked or not since it was guaranteed to work (unlike Wayland with Vulkan). This is based on the Vulkan path, which might fail if the vulkan driver doesn't support the colorspaces we need. Is it possible for the vulkan driver to not support the colorspaces we need and if so do we need to check this anywhere in the Macos display server?

--- allenwp:
The specific point that ArchercatNEO is referring to is this comment: https://github.com/godotengine/godot/pull/118076#issuecomment-4180239897

What are your thoughts, Stuart?

--- stuartcarnie:
@allenwp MoltenVK is the only Vulkan driver for Apple, which uses Metal, so it is expected to support the necessary colour spaces.


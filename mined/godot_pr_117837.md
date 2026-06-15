# PR 117837 [MERGED] — [Windows] Remove polling of SDR white level when HDR output is enabled.
AUTHOR: allenwp

## BODY
### What problem(s) does this PR solve?

- Polling of HDR luminance values every frame is slow.
- Fixes #118092
   - At least it won't flicker anymore. The brightness may still be incorrect until the player or system does something to trigger a request of `SDRWhiteLevel`, such as changing window focus away and back to the Godot window.

### What is the rationale for the approach used in this PR?

Oh, boy. Here we go:

The SDR white level on Windows is the reference white luminance used by Godot. As far as I am able to tell, the only way to adjust this value is by changing the "SDR/HDR Content Brightness" slider in the HDR section of the Windows Display Settings.

If my understanding is correct, then it is not strictly necessary to poll this SDR white level every frame. Instead, it is only necessary to check for changes in SDR white level when a Godot window regains focus. As far as I can tell, this is the behaviour exhibited by Chromium browsers, for example. Here is a video comparing this PR (bottom left) with a chromium browser (Edge, top left):

https://github.com/user-attachments/assets/31b4cdc8-a9b0-4ff9-903e-d925fe36335b

The current behaviour of checking every frame is a better user experience when the user is actively changing their SDR white level through the Windows display settings... But it is possibly a worse user experience when actually playing the game as performance may suffer if the game is CPU-bound.

Importantly, how often the SDR white level must be retrieved is very different than how often the other HDR capabilities and luminance values must be retrieved. This was discussed in detail in this thread: https://github.com/godotengine/godot/pull/94496#discussion_r2736272524 (Note: Firefox is struggling to load that conversation for me, but other browsers work fine.)

<details>
<summary>I mentioned the idea of this PR previously...</summary>

> I should mention: I believe it is not common for Windows apps to poll for SDRWhiteLevel. Normally apps will just have a hardcoded brightness in HDR and it makes for a pretty terrible user experience. Matching the SDRWhiteLevel is what will really give Godot a head above all other HDR apps/games. Conversely, polling for Max luminance is required as that changes all the time on HDR laptops because it's tied directly to the brightness control.
> 
> If the performance cost is too high to be polling for SDRWhiteLevel, we could instead check for this any time a window changes to be foreground and active. This makes for a bad user experience when adjusting brightness with the SDR Content Brightness slider, but if it's that or spending hundreds of microseconds to retrieve it from the system... well, maybe that's just a tradeoff we'll need to make :(

</details>

...but I believe the performance of this specific behaviour was never measured with the [latest optimizations](https://github.com/godotengine/godot/pull/94496#issuecomment-3881605335) that were merged into master.

### Performance

**Single monitor:** 
- Average of **71 microseconds savings.**
- Polling that has been removed with this PR would take as long as 731 microseconds or as short as 10 microseconds, which suggests that this polling can contribute to stutters.

**Dual monitor:**
- Average of **163 microseconds savings.**

<details>
<summary>Test computer specs</summary>
Mid-range gaming laptop with an i7-10750H:

Windows 11 (build 26200) - Multi-window, 2 monitors - Vulkan (Forward+) - dedicated NVIDIA GeForce RTX 3060 Laptop GPU (NVIDIA; 32.0.15.8088) - Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz (12 threads) - 15.82 GiB memory
</details>

<details>
<summary>Test procedure</summary>
I used `QueryPerformanceCounter` to measure the microseconds, saving 1000 consecutive measurements before writing them to a file for analysis.

I built the release template with the following command:
`scons platform=windows arch=x86_64 production=yes use_mingw=yes d3d12=yes target=template_release`
</details

### Was generative AI (LLM AI) used to create a portion of this PR?

No.

### Are there any parts of this PR that you are uncertain of or require special attention from reviewers?

This PR should ideally be merged before 4.7 or never merged because this sets a precedence/expectation for how the SDR/HDR content brightness Windows setting should behave in relation to Godot.

## COMMENTS
--- allenwp:
cc @DarkKilauea @blueskythlikesclouds if either of you are interested and available to do a performance comparison.

--- allenwp:
I've completed some performance measurements and updated the description text with these numbers. I think it's worthwhile to merge this PR for Godot 4.7 if no issues can be found with it through review.

--- allenwp:
> as I can't get above 1242 FPS both before and after this PR

Sounds like your test could be GPU-bound?

--- allenwp:
Good point about noting it in the documentation.

I have plans to add a subsection to the manual page under [absolute luminance values](https://docs.godotengine.org/en/latest/tutorials/rendering/hdr_output.html#absolute-luminance-values) that describes how maximum and reference luminance settings work on each platform. Since Windows is an outlier in how it handles reference luminance (shows it as “SDR Content Brightness” instead of just “screen brightness”), I need to call this out and it should be easy to add on a note about how it is only refreshed when focus is given back to Godot or the window changes screens.

Thanks for looking at this!

--- Repiteo:
Thanks!

--- Calinou:
> Sounds like your test could be GPU-bound?

Definitely not, I was testing on a RTX 5090 in an empty scene with no 2D/3D nodes and at the default window size (1152x648).

Meanwhile on Linux in the same scenario (albeit with an optimized editor binary):

<img width="185" height="33" alt="image" src="https://github.com/user-attachments/assets/94c2c47a-9e3d-42c2-93be-18586d176f25" />


--- allenwp:
Strange! Well, given this newly merged behaviour is pretty standard for a lot of windows apps, it’s probably better to run less code when possible even if it only sometimes improves performance.

Hopefully one day we can use the WinRT advanced colour events instead!

--- akien-mga:
> Hopefully one day we can use the WinRT advanced colour events instead!

You can now! WinRT was added via #116349, and you can see another example of how to use it with #116351.


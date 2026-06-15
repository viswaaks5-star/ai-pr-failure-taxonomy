# PR 118079 [MERGED] — Change embedded window options to use three stacked dots and add HDR info
AUTHOR: allenwp

## BODY
**This PR depends on #118076.** This parent PR's two commits have been included in this PR.

### What problem(s) does this PR solve?

- Closes godotengine/godot-proposals#13903
   - See this proposal for details on the problems this PR solves.
- Implements a small part of godotengine/godot-proposals#14445
- Leaves the door open for further improvements to the "embed on next play" and "make floating on next play" checkboxes, such as what is proposed in godotengine/godot-proposals#14491

### What is the rationale for the approach used in this PR?

**SDR Behaviour**

| State | Screenshot
|--|--
| Before | <img width="1497" height="305" alt="image" src="https://github.com/user-attachments/assets/b43cd1bc-13dc-425f-9321-31e8fa22a428" />
| After | <img width="1497" height="344" alt="image" src="https://github.com/user-attachments/assets/439bccc5-a573-458e-80d9-31004a086268" />

By moving the game window pop-up menu to a three dots icon, [the issue demonstrated in this stream](https://www.twitch.tv/jotson/clip/DepressedLongDonutSwiftRage-EB06N4p79C4-TClM) should be resolved, or at least mitigated until a better and more substantial change has been implemented. Placing this three dots icon next to the game window size label should be an intuitive location to find game window options, such as the embedded window sizing.

Additionally, the game window size label is now always visible when the game is running, even if it is not embedded. This change was needed for displaying HDR info when the window is not embeded...

**HDR Behaviour**

<img width="1152" height="262" alt="image" src="https://github.com/user-attachments/assets/89b74519-bf2b-485d-860a-990c9aa70aa1" />

A tooltip explains what the floating point value beside the "HDR" text represents: it's the maximum linear value. Additional HDR info is presented in this tooltip.

Importantly, no further HDR configuration options are provided beyond toggling `Window.hdr_output_requested`. In the future, a slider should be provided to allow the user to limit the output maximum linear value to preview the appearance of different screen capabilities. This should be added in a followup PR when a maximum linear value limit parameter has been added to Godot. [More details in this comment](https://github.com/godotengine/godot-proposals/issues/13903#issuecomment-4159164863).

Much of the remaining design rationale can be found in godotengine/godot-proposals#13903.

### Was generative AI (LLM AI) used to create a portion of this PR?

When starting this PR, I took inspiration from https://github.com/DarkKilauea/godot/tree/editor/hdr-game-mode, which was created using AI tools. Although I copied some of the functions and approach when starting, I have re-wrote and re-worked it to be my own.

### Are there any parts of this PR that you are uncertain of or require special attention from reviewers?

- ~~I really have no idea what I'm doing with the `TTRC` macro. Am I using it correctly throughout this PR?~~ [This has been resolved](https://github.com/godotengine/godot/pull/118079#issuecomment-4172345110)!

I've tested this to find it works well on Windows, macOS, and Fedora KDE plasma.

## COMMENTS
--- Calinou:
> I really have no idea what I'm doing with the TTRC macro. Am I using it correctly throughout this PR?

`TTRC()` means "extract this string for translation, but don't translate it immediately. Instead, let the engine's autotranslation handle it, typically in Control nodes."

`TTRC()` allows for runtime language changes without having to handle `NOTIFICATION_TRANSLATION_CHANGED` manually. Therefore, the editor tries to use it as much as possible to reduce the number of lines of code needed to support runtime language changes.

You should use `TTRC()` for text that does *not* use placeholders like `vformat()` and is part of a Control node that has autotranslation enabled (which is the default). Otherwise, you should use `TTR()` as the engine won't perform translation automatically.

--- allenwp:
Thanks, Calinou! Very helpful explanation. And it also pointed me to `TTR()`, which has some good documentation in the comments of its declaration.

I've updated the use of `TTRC()` and `TTR()` to be what I believe is correct usage.

--- allenwp:
I'm moving this back to "To Ratify" because I believe the suggestion that was provided by the reviewers to have "Loading..." written when the game is still loading is a good idea. It should also be fairly trivial to implement, so I should have it finished very shortly.

--- allenwp:
I've pushed a change to add the "Loading..." text suggestion. I also added some cleanup code to make sure that subsequent runs don't display stale information while the debugger is loading.

Because this PR depends on #118076, it shouldn't be merged until that prerequisite has been merged.

--- arkology:
<img width="464" height="216" alt="image" src="https://github.com/user-attachments/assets/e27c637b-9b43-48b3-b56b-6fce351eca80" />

Please note that "Renderer or..." line after translation will be _much_ longer and will cover a big part of screen. This is already a problem with "Make Game Workspace...", but "Renderer or..." line will make it even worse.

--- AdriaandeJongh:
Could perhaps be shortened to 'rendering driver'.

--- allenwp:
I’ll change it to just be “Renderer”, since the rendering device driver is a configuration of the renderer.

I’ll also see if I can add a tooltip to these error labels that gives some instruction to the user on how to resolve this. It would include mentioning changing the renderer or rendering device driver for this error.

--- allenwp:
I've adjusted the text to be shorter and added tooltips for instructing the user on how to change things to allow for HDR output:

<img width="533" height="203" alt="image" src="https://github.com/user-attachments/assets/173719a6-1d9a-4051-a99c-d88eaf4d3ab1" />

<img width="417" height="169" alt="image" src="https://github.com/user-attachments/assets/6829f0f7-a205-4668-b427-513bb4cb2b4b" />

Tooltip for when the display server doesn't support HDR output is:
> Try changing the display/display_server/driver
> advanced project setting to a display server
> that supports HDR output."

I believe this resolves all outstanding comments.

Edit: hmm, maybe I should write “Change…” and “Move…” instead of “Try changing…” and “Try moving…”

--- allenwp:
Sorry, it always takes me a few tries to get wording of user-facing text into an optimal state. I've pushed an update to tooltip text:

<img width="272" height="106" alt="Screenshot 2026-04-06 at 3 00 17 PM" src="https://github.com/user-attachments/assets/01e0c243-775a-43b6-9b94-833345d2c693" />
<img width="275" height="97" alt="Screenshot 2026-04-06 at 3 05 11 PM" src="https://github.com/user-attachments/assets/4f692cf5-8378-4967-ad72-cd44b7f4c89d" />
<img width="318" height="116" alt="Screenshot 2026-04-06 at 2 52 08 PM" src="https://github.com/user-attachments/assets/26b4a4ee-0454-41b1-8fe1-4ae0223951ee" />


--- Repiteo:
Thanks!

--- DySeath:
> By moving the game window pop-up menu to a three dots icon, [the issue demonstrated in this stream](https://www.twitch.tv/jotson/clip/DepressedLongDonutSwiftRage-EB06N4p79C4-TClM) should be resolved, or at least mitigated until a better and more substantial change has been implemented. Placing this three dots icon next to the game window size label should be an intuitive location to find game window options, such as the embedded window sizing.

I don't think it mitigates the issue shown in this stream and, in fact, makes it harder to discover in some cases.

Assuming I'm not missing something obvious:
In the editor, the "window size label" is not visible. When running the game in non-embedded mode, it is not visible either because you would be focusing on the extracted game and not on the game tab in the editor.
It seems to be the case for the streamer you've shared since both "Embed Game on Next Play" and "Make Game Workspace Floating on Next Play" are disabled in the stream segment you've shared when he finally finds the setting.

Running the game in non-embed mode seems necessary when you want to record only the game. For example, I'm not a streamer but I make a short recording every day for my teammates with OBS, so I have to deactivate it.

I think for this use case, the three dots in the far right corner looks like settings for this part of the editor UI, instead of other settings for the game view itself, since they are separated from other game view settings.

I think the issue can be mitigated by aligning both window size and the three dots on the left with other game view settings.

I agree this issue will be solved if this proposal (https://github.com/godotengine/godot-proposals/issues/14445) is implemented but for the time being it seems a usability regression to me.

For context I've tested in both 4.7 beta1 and 4.7 beta2.

I hope this message is clear enough and it helps. Thank you for your work. It is still very much appreciated.

--- vaner-org:
Now that we've entered RC stage, and neither #118664 nor an implementation of [godot-proposals/#14491](https://github.com/godotengine/godot-proposals/issues/14491) are making it to 4.7, would it be acceptable to revert the position and icon of the embedded window options back to the left side? It seriously impedes discovery, and much of the options contained within will more than likely move again in a following version.

I'm also unsure why the HDR subsection is hidden entirely when the game isn't running...

> <img width="424" height="202" alt="image" src="https://github.com/user-attachments/assets/b7a24305-4ad1-43ed-a20a-376b78e6f7cc" />

Isn't this really bad for discovery of this new feature too?

Can the HDR options not become persistently visible and remain here, while the rest of the options be restored to their original location/icon, pending planned improvements?


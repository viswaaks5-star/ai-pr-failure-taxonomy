# PR 117754 [MERGED] — Hide renderer selector in main editor window and add editor setting
AUTHOR: allenwp

## BODY
## For users upgrading to 4.7

The renderer selector is now hidden by default. As always, you can change your project’s renderer by changing the `rendering/renderer/rendering_method` project setting.

If you need to change your project’s renderer often, you can show renderer selector in the editor’s main window by changing the `interface/editor/appearance/show_renderer_selector` editor setting.

### What problem(s) does this PR solve?

1. The renderer selector takes up precious real estate on the main Godot editor window while not being used by most users.
2. The renderer selector adds visual complexity to the main editor window for new users.

### Does this PR include any additional changes beyond those required to solve these problems?

- This PR adds a new editor setting to restore existing behaviour for users who have a project that targets multiple renderers and use the renderer selector often during authoring to tweak the appearance of scenes.

### What is the rationale for the approach used in this PR?

**Design**
This PR prioritizes user experience.

This means that it does not prioritize the Godot developer experience: The renderer can no longer be seen in screenshots or screen recordings of the main editor window, which may make it slightly more difficult for Godot developers to debug issues that are discovered through screen recordings and screenshots rather than issues that have been reported using the "Copy System Info" text. I believe that the design and approach to including additional debug information in the main editor window or title bar should be handled in a separate PR, such as #103042 or that renderer information should never be visible on the main editor window or title bar to ensure that there is less visual noise for new users.

**Technical**
Because the renderer cannot be changed without restarting the editor, all configuration of this `OptionButton` can simply remain in the `EditorNode` constructor. The initial setting of visibility of this control is moved to be the final step of setup for this control to ensure consistent behaviour of setup regardless of the setting (both now and in the future if anything relating to the setup of this control is changed).

### Was generative AI (LLM AI) used to create a portion of this PR?

No.

### Are there any parts of this PR that you are uncertain of or require special attention from reviewers?

As [demonstrated in this comment](https://github.com/godotengine/godot/pull/103042#pullrequestreview-3987253242), the renderer selector could be implemented instead as a plugin, so it's possible that the renderer selector could be removed entirely from Godot. I have chosen to not go with this approach because this will make for a less optimal workflow for users who switch often during authoring as [described in this comment](https://github.com/godotengine/godot/pull/103042#issuecomment-4085934771).

_Bugsquad edit: Closes https://github.com/godotengine/godot-proposals/issues/11806_

## COMMENTS
--- Repiteo:
Thanks!

--- QbieShay:
Hi 👋 engine dev here. I switch between rendering backends a lot to make sure i don't break stuff. Any chance we can make this a bit less clicks? For example as an entry in this menu? 
<img width="411" height="307" alt="image" src="https://github.com/user-attachments/assets/bc004f74-c004-4473-bd04-f4f29c914c0e" />


--- QbieShay:
Nevermind, I should have read the discussion above to figure out how to bring it back. Found it.

--- allenwp:
I added a note at the top of this PR’s description to make this info easier to find.

--- Copperplate:
> If you need to change your project’s renderer often, you can show renderer selector in the editor’s main window by changing the interface/editor/appearance/show_renderer_selector editor setting.

Thank you, Allen!! I appreciate you leaving that option available. I do like seeing at least some form of text confirmation for both version number and renderer (though it's true the Output Dock shows this in every play session), and I also totally understand wanting to free up screen real-estate. You made a great solution that solves all issues while keeping everyone happy! :-)


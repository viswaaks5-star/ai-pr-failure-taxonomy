# PR 116640 [MERGED] — Add `custom_maximum_size` property to `Control`
AUTHOR: StarryWorm

## BODY
* Closes https://github.com/godotengine/godot-proposals/issues/13534
* Supersedes/Alternative to https://github.com/godotengine/godot-proposals/issues/8333, https://github.com/godotengine/godot-proposals/issues/13568 , #94171, #112364

Adds a `custom_maximum_size` property to `Control`. This property will limit the size of the `Control`.
This property is `Size2`, and only applies to dimensions for which it is greater than or equal to 0.
* e.g., `custom_maximum_size = (100,0) will limit the width to 100 but will not limit the height.

This property is directly exposed in the Inspector and can be modified freely. The `custom_maximum_size` property **overrides** `custom_minimum_size` if it is smaller. 
* e.g., `custom_minimum_size = (100, 100)` with `custom_maximum_size = (200, 50)` will result in `size = (100, 50)` (expandable to `(200,50)` if needed by its contents)

Furthermore, a new `propagate_maximum_size` boolean property is added to `Control`, which forces all children to respect the `custom_maximum_size` defined on that `Control`.
* Default value: `false`.
* This is overridden to `true` for `Container`.
  * This is further overridden back to `false` for `ScrollContainer`. 

Certain `Container` subtypes may limit the size of their children even further than the maximum size in order to bring the behavior in line with existing minimum size behavior.
* For example, a `MarginContainer` with a child with `size = (50,50)` and margins of 5px on every side will have `size = (60,60)` currently. In this PR, if a `MarginContainer` has `custom_maximum_size = (60, 60)` with 5px margins, the children will have `maximum_size = (50,50)` (when `propagate_maximum_size = true`)

<details>
<summary> List of affected `Container` subtypes and details </summary>

`FoldableContainer`: now takes into account the [`panel`](https://docs.godotengine.org/en/stable/classes/class_foldablecontainer.html#class-foldablecontainer-theme-style-panel) theme property.
`MarginContainer`: now takes into account [`margin_*`](https://docs.godotengine.org/en/stable/classes/class_margincontainer.html#class-margincontainer-theme-constant-margin-bottom) properties.
`PanelContainer`: now takes into account the [`panel`](https://docs.godotengine.org/en/stable/classes/class_panelcontainer.html#class-panelcontainer-theme-style-panel) theme property.
`ScrollContainer`: now takes into account the [`panel`](https://docs.godotengine.org/en/stable/classes/class_scrollcontainer.html#class-scrollcontainer-theme-style-panel) theme property and works with [`SCROLL_MODE_RESERVE`](https://docs.godotengine.org/en/stable/classes/class_scrollcontainer.html#enum-scrollcontainer-scrollmode).
`TabContainer`: 
* For the tabs themselves: now takes into account the [`panel`](https://docs.godotengine.org/en/stable/classes/class_tabcontainer.html#class-tabcontainer-theme-style-panel), the [`tabbar_background`](https://docs.godotengine.org/en/stable/classes/class_tabcontainer.html#class-tabcontainer-theme-style-tabbar-background), and the [`TabBar`](https://docs.godotengine.org/en/stable/classes/class_tabcontainer.html#class-tabcontainer-method-get-tab-bar) itself.
* For the tab bar: now takes into account the [`tabbar_background`](https://docs.godotengine.org/en/stable/classes/class_tabcontainer.html#class-tabcontainer-theme-style-tabbar-background), and the [`tab_separation`](https://docs.godotengine.org/en/stable/classes/class_tabcontainer.html#class-tabcontainer-theme-constant-tab-separation).
</details>

The second commit enables `ScrollContainer` to make use of this new `custom_maximum_size` by adding a new `SCROLL_MODE_MAXIMIZE_FIRST`. This new mode makes the `ScrollContainer` increase its `size` to fit the contents up to its `custom_maximum_size` first, and if the contents are larger than `custom_maximum_size`, it behaves like `SCROLL_MODE_AUTO`. If no `custom_maximum_size` is defined for that axis, it will behave like `SCROLL_MODE_DISABLED`.

The third commit enables `Label` and `RichTextLabel` to work with the new `custom_maximum_size`. This new behavior will override the old behavior of `custom_minimum_size` if both are defined. Old behavior (when only `custom_minimum_size` is defined) is preserved. 
* For `Label`, this is relevant when `autowrap_mode != AUTOWRAP_OFF` or when `text_overrun_behavior != OVERRUN_NO_TRIMMING`
* For `RichTextLabel`, this is relevant when `fit_content = true` and `autowrap_mode != AUTOWRAP_OFF`

> [!WARNING]
> Merge notes: This PR and #112741 are interlinked. The code section in question is the addition of `custom_maximum_size` to size computation in `Control::_size_changed` (this PR), which becomes `Control::_compute_position_and_size_with_grow` (that PR)

*AI disclaimer: GPT Codex 5.3 was used to help me figure out some of the `ScrollContainer`, `Label`, and `RichTextLabel` implementations. All AI-generated content was thoroughly reviewed by me and tested piece-wise. Most of the implementation is human-made.*

## COMMENTS
--- markdibarry:
I tested again after the changes to `Label` and `RichTextLabel`, and this does work now in certain specific scenarios. `Label` seems to ignore the parent's max size, and `RichTextLabel` still doesn't work at all. For `Label`, it *does* appear to work if you set both the parent's max size and each individual descendant `Label`'s max size to the exact same value, but that's not very feasible as a workflow and leaves a lot of undefined and buggy behavior.

--- StarryWorm:
That should solve it. It was a stupid bug because I used `get_custom_maximum_size()` instead of `get_combined_maximum_size()`. Only the latter uses the parent `Control`'s `custom_maximum_size` if `propagate_maximum_size` is `true`.

--- markdibarry:
I don't believe there should be any case where `propagate_maximum_size` should ever be `false`, so I don't think there's a need for that new boolean. Either way, I tried with both on and off, and it's still the same behavior.

So that you can test it too, going forward, here's the steps to recreate the scenario mentioned in all the proposals for this feature (I'd make an MRP but since the internal code is still a WIP, it's more reliable this way):

1. Create a new `Control` scene and add a `PanelContainer`.
2. Set the `PanelContainer`'s `custom_maximum_size` width to 150px and set its horizontal container sizing to Shrink Begin
3. Add a `VBoxContainer` as a child of the `PanelContainer`
4. Add one or more `Label`s with auto wrap or text overrun set to the `VBoxContainer`.

As you type notice that it ignores the `PanelContainer`'s max size.

--- StarryWorm:
> I don't believe there should be any case where `propagate_maximum_size` should ever be `false`, so I don't think there's a need for that new boolean. Either way, I tried with both on and off, and it's still the same behavior.

As stated in the PR description, some `Control` subtypes need it to be false. This includes `ScrollContainer`, for example, and is basically every `Control` that has `clip_contents = true` by default. 
I could very well modify the PR to set `propagate_maximum_size = true` as the default behavior and override it to `false` for the affected containers. 

Regarding your example, it actually works as intended. If you look at your `Label`, you will see it still shows the warning for the max width being needed. That is because the `VBoxContainer` does not have `propagate_maximum_size` set to `true`. If you turn that on, it will work as you are expecting it to. 

So this isn't a bug, it's a UX problem. 
With this, I think it's pretty clear that I should set it to `true` by default, with `false` overrides for the specific `Container` subtypes that need it. 
* Edit: This may not be possible in the event that upgrading an existing project containing said subtypes doesn't set it to `false` at upgrade-time. Will test before changing default behavior. 

The propagate flag will still only be for immediate children, but with `true` by default, it should make the new feature "work as expected" by default. It absolutely cannot be for more than the immediate children (i.e., grandchildren, etc) due to the same reason why it exists. Those subtypes will pretty much break otherwise. 

If you want to see it for yourself, just create a `ScrollContainer` with a `custom_maximum_size` and `propagate_maximum_size = true`, and put anything as a child with a `custom_minimum_size` greater than the scroll's max size (or a box container filled with more children than fit in the `ScrollContainer`'s immediately visible rect). When you run the scene and scroll, it will scroll to nothing instead of the expected contents. 

--- markdibarry:
I do see now that it *does* work but only for immediate children, which you're right, is just not a good workflow/UX yet. It absolutely should have all descendants respect the value, and that should be the default. We wouldn't want it to break compatibility (or this PR would probably have to wait until we have a consensus on that), so whatever the defaults would be would need to show no change to existing projects. Considering max size just doesn't exist atm, no value should be the same behavior as without this PR. 

I think, because this is a wide-reaching change that will require a lot of testing, it may be good to include a test project so we can see how it behaves with different workflows, especially the ones outlined in the proposals (so they can be closed). The two main ones are the one I had above about multiple `Label`s in a `PanelContainer` (closes #13534, #13568), and the second would be the `ScrollContainer` one ([#94171](https://github.com/godotengine/godot/pull/94171)) where content should make it grow to a max size, then create a scrollbar from then on.

I haven't tested the `ScrollContainer` one, but I imagine it wouldn't work without changes to `ScrollContainer` as well, but to avoid this getting too out of hand, maybe we could handle that in a follow up PR. I may be wrong though.

--- StarryWorm:
Changed the default value of `propagate_maximum_size` to `true` for UX. 

This is overridden to `false` for `GraphEdit`, `ItemList`, `RichTextLabel`, `ScrollContainer`, and `Tree`. All of these `Control` subtypes have `clip_contents` set to `true` by default, as their children may be bigger than themselves yet still navigated (primarily through scrollbars) within the bounds of the parent.

* This will work with upgrading projects.
* These changes are all in the main commit instead of separate commits to prevent any sort of regression issues if any of the separate commits were reverted for any reason. One commit is responsible for introducing the new `custom_maximum_size` and ensuring no existing projects break due to it.

@markdibarry please try your scenario again and let me know if it fails. Works as "would be expected" on my machine. 

> The two main ones are the one I had above about multiple Labels in a PanelContainer (closes https://github.com/godotengine/godot/issues/13534, https://github.com/godotengine/godot/issues/13568)

Yep, which now should work fully as expected.

> the second one would be the ScrollContainer one (https://github.com/godotengine/godot/pull/94171) where content should make it grow to a max size, then create a scrollbar from then on.
> I haven't tested the ScrollContainer one, but I imagine it wouldn't work without changes to ScrollContainer as well, but to avoid this getting too out of hand, maybe we could handle that in a follow up PR. I may be wrong though.

This is already handled with the new `SCROLL_MODE_MAXIMIZE_FIRST` 😄 

--- StarryWorm:
Regarding tests, I will add unit tests to the engine for the scenarios to help guard against regressions in the future, and will provide a test project so people can see for themselves how it works. 

--- markdibarry:
*(chef's kiss)* Wunderbar. Tested on those two scenarios and both are working as expected!

Wasn't trying to nitpick, just wanted to make sure it covered both of those two proposals completely. I just know first hand if it doesn't "just work" for 90% of cases out of the box, there's gonna tons of confusion from users and an avalanche of issues created around it. This seems like, at least while we trial run:
1. A user will need to mess with the max size initially for there to be any chance of them messing something up, and can just set it to its defaults to fix it.
2. When they *do* use it with specific purpose, the defaults work as expected for the majority of cases.
3. For the ones that need special custom behavior, they can modify it.

Now that we can see the main cases covered, we can dig in further for regressions and refine the workflow.

Great work!

--- StarryWorm:
Oh, don't worry, I am absolutely delighted you pushed the PR to its limits. Nitpicking is why the PR process exists. 

Ideally, given how this is set up, there is 0 chance of regression. All the tests also run fine on my machine, which should cover any potential regressions due to this change. As said, though, I will add as many tests as I can think of, both to prevent regressions caused *by* this PR and future regressions *against* this PR.

--- StarryWorm:
Added unit tests for everything - in the appropriate commit for all of them.

--- StarryWorm:
Regarding documentation, I have added it to the properties for which it is relevant. 

I don't think adding a paragraph at the top of the documentation for the classes (`ScrollContainer`, `Label`, `RichTextLabel`) is the right decision. 
Currently, this isn't the case for any property on those classes (or most other classes), and I think that's a good standard to follow. Even the minimum size handling for `Label` was not documented at the class level (or at all, to be fair); it was just a warning.

Also, since we are getting closer to a PR ready for merging, I want to make sure the commits are okay as is. I have it split into three because they all do something "separate": adding a `Control` feature, a `ScrollContainer` feature, and a `Label`/`RichTextLabel` feature. I know the standard is to keep things in one commit unless there is a very good reason not to. I believe these split commits meet that standard.
Maintainers, what's your opinion? Should I squash them?

--- StarryWorm:
> It propagates the max size to individual nodes which is a bit weird in the context of BoxContainers

How is it weird? The contents of a `BoxContainer` are always smaller or as large as it (i.e., one child is visible). Currently, this is handled by the `BoxContainer` expanding to fit its contents. If we don't have it propagate its max size to its children, it will not layout as expected. Or am I missing something?
*This applies to all `Container` types with the exception of `ScrollContainer`.*

> and it also propagates to grandchildren and beyond, even if those children are not in a container. [...] something that may confuse new users (eg. "why aren't my labels growing?! ohh it's because 6 parents up something propagated all the way down here")

I don't really see a real-world use case for this. I could be missing some, but as far as I understand it, `Container` types are meant to "contain" all their children and grandchildren, i.e., they should all fit within the `Container` rect. 
If some users are creating some kind of (in my opinion) counter-intuitive layout where that isn't the case, I would frankly put the onus on them. Also, they aren't "new" users at that point. 

Now, what could be done is to make `Control` not propagate by default, and instead have `Container` override that. I would actually prefer that. After all, `Control` types aren't meant to "contain", that's what we have `Container` types for.
*For a much better explanation of what I am trying to say, see https://github.com/godotengine/godot-proposals/issues/14222*

Not having it propagate for `Containers` is, in my opinion, the wrong decision. 
The moment you add `MarginContainers` and `BoxContainers` to a UI sub-element (example: a side panel in a 2D UI), you would need to go through each of their children, and calculate what max size each of them needs (including the margins from their parents and their siblings in `BoxContainers`) so that your UI sub-element ends up being the right max size and not infringe on the rest of the UI/the gameplay area. 
Or you can just give the UI sub-element the constraint it needs to follow, and the rest will arrange itself to match it.

Edit: I strongly believe the user should still be able to toggle propagation on or off for more advanced layouts. This also goes back to Yuri's proposal of merging `Control` and `Container`, which is all about giving the user the choice of how to handle things. 

*Side note: This reminds me that I need to specialize `MarginContainer` and add in logic for any other `Control` that can end up with margins to substract that from their child's combined maximum size if propagate is on.*

--- markdibarry:
@AdriaandeJongh To piggy-back off what StarryWorm was saying, the behavior you're suggesting sounds more confusing to users tbh. I agree that ideally we could avoid the bool if possible, but the intuitive behavior IMO is children of a container with `custom_maximum_size` should respect the size of their container. I think of it from a UX perspective:

- The most likely scenario is you don't need `custom_maximum_size`, in that case don't use it! Simple.
- The second most likely (the proposal scenarios) is that you need it so that a `Control` or `Container` and children need to not exceed a maximum size. In this case (in the current form), it does it by just setting the `custom_maximum_size` of the `Control` or ancestor `Container`. Simple!
- The least likely is that you need a maximum size for *one single* `Control`, and it *does* have children, and *those* children need to exceed the maximum size of its container. In that case, it should be able to be overridden on a per-node basis.

What you suggest means more consistency at the cost of the common scenario and uncommon scenario both being complex to use. I guess we'd have to determine which we're more comfortable with. The `HBoxContainer` example you used seems like an uncommon case in UI (at least vs a `VBoxContainer`), but you probably wouldn't use a max size to achieve that anyway (unless I'm misunderstanding the example). I don't think there's really a way to know what the user *intends* to happen when you have a bunch of labels in an `HBoxContainer` and all of them set to auto-wrap without setting the labels min/max sizes themselves.

> Now, what could be done is to make Control not propagate by default, and instead have Container override that. I would actually prefer that. 

@StarryWorm Yeah, that makes sense to me.

--- StarryWorm:
Changelog:
* `propagate_maximum_size` is now `false` by default, overridden to `true` by `Container`.
  * This is still overridden to `false` for `ScrollContainer`.
  * `Control` subtypes that had a `false` override no longer have it (unnecessary).
* Updated documentation to reflect that `update_maximum_size` calls `update_minimum_size` internally.
  * Modified two calls in `Control` that used to be `update_minimum_size` and `update_maximum_size` to only `update_maximum_size` to avoid double calling of `update_minimum_size`. This does not change behavior. 
* Certain `Container` types now use a new `get_inner_combined_maximum_size()` to reflect that their content's maximum size should be limited more than just by the `Container`'s combined maximum size.
  * This brings the behavior in line with the reasonable expectation, namely that it works like minimum size works, whereby the parent `Container` expands to include all its children and additional theme elements.
  * This behavior was not brought to any `Control` types, as they currently don't have the minimum size behavior that this reflects.

<details>
<summary> List of affected `Container` subtypes and details </summary>

`FoldableContainer`: now takes into account the [`panel`](https://docs.godotengine.org/en/stable/classes/class_foldablecontainer.html#class-foldablecontainer-theme-style-panel) theme property.
`MarginContainer`: now takes into account [`margin_*`](https://docs.godotengine.org/en/stable/classes/class_margincontainer.html#class-margincontainer-theme-constant-margin-bottom).
`PanelContainer`: now takes into account the [`panel`](https://docs.godotengine.org/en/stable/classes/class_panelcontainer.html#class-panelcontainer-theme-style-panel) theme property.
`ScrollContainer`: now takes into account the [`panel`](https://docs.godotengine.org/en/stable/classes/class_scrollcontainer.html#class-scrollcontainer-theme-style-panel) theme property and works with [`SCROLL_MODE_RESERVE`](https://docs.godotengine.org/en/stable/classes/class_scrollcontainer.html#enum-scrollcontainer-scrollmode).
`TabContainer`: now takes into account the [`panel`](https://docs.godotengine.org/en/stable/classes/class_tabcontainer.html#class-tabcontainer-theme-style-panel), the [`tabbar_background`](https://docs.godotengine.org/en/stable/classes/class_tabcontainer.html#class-tabcontainer-theme-style-tabbar-background), and the [`TabBar`](https://docs.godotengine.org/en/stable/classes/class_tabcontainer.html#class-tabcontainer-method-get-tab-bar) itself. 
</details>

--- AdriaandeJongh:
Wanted to test this again but the Scene and FileSystem panels are broken so I can't do anything to test this 😅

EDIT: I downloaded the artifact for macOS editor. I don't know whether it's this PR or another PR in master that broke these panels.

<img width="554" height="228" alt="Screenshot 2026-02-27 at 11 42 36" src="https://github.com/user-attachments/assets/e7401200-8005-4f29-aa36-afab91a8be5c" />
<img width="391" height="234" alt="Screenshot 2026-02-27 at 11 42 41" src="https://github.com/user-attachments/assets/44ea1e72-6522-4ea2-9b39-dd00131dd945" />


--- StarryWorm:
That's odd... The Windows editor artifact (which has the same compilation flags that could impact this) doesn't have that issue. The implementation should be completely platform independent too... :/

Clearly a `ScrollContainer` issue, though, which I think is this PR's fault; one of the builds I made during the development of the feature had that issue, but I resolved it... or so I thought, I guess? 

--- jelolul:
> That's odd... The Windows editor artifact (which has the same compilation flags that could impact this) doesn't have that issue. The implementation should be completely platform independent too... :/

I've actually tested this and I have the same issue on the Windows editor artifact

--- StarryWorm:
Wait what? Now I'm very confused... 
Could you please tell me how you got to that state? 

I did:
* Download windows editor from Checks tab
* Unzip, run it
* Opened existing project -> works
* Created new project -> works
  * Tried with all 3 renderers, compatbility, mobile, and forward+

--- AdriaandeJongh:
> Wait what? Now I'm very confused... Could you please tell me how you got to that state?
> 
> I did:
> 
> * Download windows editor from Checks tab
> * Unzip, run it
> * Opened existing project -> works
> * Created new project -> works

This is precisely what I did.

--- jelolul:
> * Download windows editor from Checks tab
> * Unzip, run it
> * Opened existing project -> works

These exact same steps, I tested and it happens even when I create a new project.

I'm confident that it broke after the last changes that you made 2 days ago.

--- StarryWorm:
I mean, I have a rough idea of what could have caused the issue. 
The problem I am having right now is figuring out why it works on my machine and not on yours (plural), even though it's the same artifact. The only way I have to ensure it all works now is to run it through CI and have you two check the artifacts...

--- StarryWorm:
Problem identified: the Modern theme is what breaks it. My editor runs on the Classic theme (not a fan of the Modern), and it works with that one.
Should be an easy fix

--- StarryWorm:
Fixed, also included the language changes from @markdibarry and @AThousandShips 

--- StarryWorm:
The expand flag is not implemented in this PR. It was implemented in the `SizeContainer` PR, and I haven't ported that over. That means it still behaves as before, and (from what I tried) does not produce any 'undefined' behavior. 

I could implement it in this PR, or it could be added in a separate follow-up PR if desired. The expected behavior would be something like this (in my opinion):
* The child `Control` with expand on would increase its size on that axis up to the maximum allowed by `combined_maximum_size` if that is not `(0, 0)`.

This naturally incorporates the parent's restraint put, as well as the child's own `custom_maximum_size`. It would layout exactly the same way as it currently does, based on the size flags.

--- AdriaandeJongh:
> The child `Control` with expand on would increase its size on that axis up to the maximum allowed by `combined_maximum_size` if that is not `(0, 0)`.

AFAIK it already does this. What I meant with 'undefined' position is that there is currently no way to configure the position of a child that is meant to expand but limited by the custom maximum size. For instance, a HBoxContainer child that horizontally expands but has a custom max width will align itself to the left, even if the HBoxContainer defines that the children should begin at the end (and thus, at the right).

--- StarryWorm:
What I meant regarding the expand, is that the parent will not expand to its `custom_maximum_size` if the child has expand flag on. For example this `HBoxContainer` 
<img width="677" height="656" alt="image" src="https://github.com/user-attachments/assets/52534a7d-2c20-443f-a76d-30279fed7d60" />
should expand to 100 width since one of its children has expand flag
<img width="652" height="226" alt="image" src="https://github.com/user-attachments/assets/aa8dd1d5-d38f-4c93-87a2-4be196e24685" />
but it currently does not. 

As a user, I would expect that the expand flag... expands the container if it has a max size. 

--- StarryWorm:
> For instance, a HBoxContainer child that horizontally expands but has a custom max width will align itself to the left, even if the HBoxContainer defines that the children should begin at the end (and thus, at the right).

Ok, I see the issue after some testing, will fix. That's a proper bug. 


--- StarryWorm:
That turned out to be a much bigger fix than expected. The issue wasn't only the final positions, but also that a lot of empty space could be created that the other expanding children wouldn't occupy. This issue was the real kicker and applied to more subtypes. 

Fixed the issue for `BoxContainer`, `GraphNode`, `FlowContainer`, `GridContainer`, and `ScrollContainer`.

Have not included the language changes yet since we are still discussing how to word the whole thing with regards to propagation ([see comment](https://github.com/godotengine/godot/pull/116640#discussion_r2867517581))

--- StarryWorm:
Had to fix a CI bug so I added the language stuff that is not still being discuessed

--- StarryWorm:
1. I will look into that. Ideally, fill should ... fill
2. That's definitely a bug. 
3. It does nothing... I guess I could put a limit in the setter to limit it to 0, but it doesn't matter. The documentation also states that 0 or negative does nothing, so I don't think it needs changing. 
4. Nice!

*Note: I will be travelling for a bit over a week, starting in about an hour, so it might take a little time for me to get around to fixing 1 and 2 and the PR, thus being ready for merge. Depends on the plane's Wi-Fi quality and my schedule.*

--- AdriaandeJongh:
> 1. I will look into that. Ideally, fill should ... fill

Yeah but in this case I did add a maximum vertical size, so it makes sense that it _doesn't_ fill. So it really is just about the fact that because it doesn't fill, now it also has a position... that you can't control. I don't think there's a way around this, conceptually, unless we introduce size flags for `size_flags_horizontal` and `size_flags_vertical` that allow to expand AND position begin / center / end, which will only make sense in this very specific context... idk, feels gross.

> 3. It does nothing... I guess I could put a limit in the setter to limit it to 0, but it doesn't matter. The documentation also states that 0 or negative does nothing, so I don't think it needs changing.

I'd put a limiter on it. That way users never have to wonder whether negative values do anything.

Safe travels!


--- StarryWorm:
> unless we introduce size flags for size_flags_horizontal and size_flags_vertical that allow to expand AND position begin / center / end, which will only make sense in this very specific context... idk, feels gross.

Or we just add expand as an option, so that shrink begin/center/end all allow it to still expand up to its maximum size. 

> I'd put a limiter on it. That way users never have to wonder whether negative values do anything.

Yeah sure

--- StarryWorm:
* "Fixed" 3. 
* Fixed 2. This resulted in the same problem for `GridContainer` as `BoxContainer` suffers from. With `GridContainer`, the children already have access to the expand flag in both dimensions, so I decided it would be really stupid to not make it work with the shrink flags. So now it does. (fixed via `control.cpp`)
  * Took the opportunity to add `GridContainer::_resize`, reflecting the implementation in all other `COntainer` subtypes. This causes what seems like a massive change in that file but I really added like 5 lines of code to fix the issue, the rest is just moving the method over. Git doesn't like showing it as what it is - mostly whitespace - because of those added lines in the middle which completely throw it off.
* Fixed 1. Since now I had the implementation from the 2 fix, all it took was to add the expand flag in both dimensions regardless of orientation. So i did. This flag does absolutley nothing if the child is in fill mode or if it doesn't have a custom maximum size, resulting in no compatibility breakage. 

--- markdibarry:
@AdriaandeJongh I'm not sure if you can also replicate this, but I attempted the same scene as your screenshots (it looks like full rect anchors on the `Control` and `HBoxContainer`), but it seems if I *don't* override any defaults on any descendants of the `HBoxContainer`, and set the `HBoxContainer`'s max size, it shifts it by a certain amount. I can't figure why this would be intentional.

https://github.com/user-attachments/assets/9064a7e8-976e-45da-bf1a-4386e144cf92

I imagine there will be more of these oddities as we go, which IMO isn't a deal-breaker. The two things that are paramount (IMO) are:
* Does it fill Godot's current limitations described in the proposals?
* Are there any regressions? i.e. Bugs or performance issues if you *don't* set `custom_maximum_size` compared to the main branch

I'll spend more time testing this today, but the majority of my testing will be focused on those two areas. With how complex Godot's UI system is, it would surprise me if there aren't many issues surrounding this created in the future, both for bugs and for need of clarification. But it *is* a gap, so I'd rather it filled than not if there's no drawbacks for those not using it.

That being said, it'd be great if anyone more familiar with accurately testing performance could comment on the addition of these two new properties for every `Control`. Sidebar tangent: `Control`s are already heavy by nature (compared to `Node`s), so I would say that it's not going to be an iceberg for someone who already has 100 nested `Control`s for their UI. I've seen other proposals that are looking to encourage using less `Control`s altogether, which is the better way forward. It'd be less important to reduce the performance of each of your 100 `Control`s by 1% if you can allow users to create the same UI using 40-50% less `Control`s altogether. But that's a separate convo.

--- StarryWorm:
This might not be solvable within the scope of this PR, even if it may be caused by it. I will have to take a look.
The reason I say this is that there are known issues with anchors and positioning within `Control`, which #112741 attempts to fix.
*Maintainers: please do look at that PR too, the amount of small bugs that exist with regards to anchoring and positioning is enough to drive one up the wall once you notice them. My old PR, which is an alternative linked in that PR, has some videos showing the issues.*

--- StarryWorm:
From what I could find, fixing this issue would require changes beyond the scope of this PR. 
If, once this PR and #112741 are merged, the issue persists then I will have to do a deeper dive and figure it out. 

--- KoBeWi:
> it seems if I don't override any defaults on any descendants of the HBoxContainer, and set the HBoxContainer's max size, it shifts it by a certain amount.

The maximum size you set is smaller than the parent Control, so the HBoxContainer tries to fit a full rect up to its maximum size, making it centered. The child nodes will stick out, because the HBoxContainer/PanelContainer don't have any way to handle overflow.

The unexpected part is that enabling trimming/wrapping in Labels does not resolve this. The combined maximum size of each Label is equal to that of HBoxContainer's, instead of being divided. This behavior can be improved (although can be in a follow-up, depending on complexity).

--- StarryWorm:
Just naively dividing the `BoxContainer`'s max size by its number of children and then assigning them that division result will just cause wrong behavior.

The only way I see of solving this issue is that `SizeContainer` gives priority to the first child, then the second,  ..., until the last. So the first child (`Label` in your example) would compute its size, which then gets subtracted from the `SizeContainer`'s max size that gets passed to its n+1 children. Repeat till filled. 
This way the nth child would have a size that is cropped to fit. The big issue, though, is for that child's children. They won't see that new size constraint, and it is impossible within the current system to make them see it. 

The system needed to make that work would be a complete rewrite of the `get_combined_maximum_size()` system to instead have a cached `parent_maximum_size` value instead of calling `parent->get_inner_combined_maximum_size().min(parent->get_combined_maximum_size())`, which `BoxContainer` could then set during `_resort()` (and which would be set in `Control::add_child_notify()` for the existing PR behavior).

But I'm not sure if that behavior counts as A. expected nor B. desired. I would assume that implementing something like this could cause a lot of questionable new edge cases.

Let me know your thoughts, and if the consensus turns out that yes, we want it, then I'll patch it in. I don't particularly have a strong opinion for or against. 

--- StarryWorm:
There we go. This change turned out to be a bit more than expected. Here's the changelog:
* Parent maximum size handling was changed from the child querying the parent to the parent setting a value on the child.
* The ignore value is now `Size2(-1, -1)`
  * This means the default is also now `Size2(-1, -1)`
  * When setting `custom_maximum_size` to any negative value, it automatically caps to `Size2(-1, -1)`
  * This change is required to give parents the ability to completely suppress a child to `Size2(0, 0)` if needed
* `Control::get_combined_minimum_size()` no longer accounts for the value returned by `get_combined_maximum_size()`
  * This was causing update suppression, which is a major issue
* `BoxContainer` and `GridContainer` now clip their children to their rect if a maximum size is defined. 
  * This uses the new `Size2(0, 0)` supression behavior. Thanks to this, it is respected down the tree for all descendants of the children.
  * Reminder: the diff for `GridContainer` looks much worse than it is. I only added about 20~30 lines of code, but since the `_resort()` method was extracted from `_notification()`, git really doesn't like the two having happened at once...
* `TabContainer` now properly limits the `tab_bar`'s size
* `TabBar` now properly respects its maximum size
  * It also properly respects `clip_tabs` being enabled and the buttons showing when limiting the text length.
  * Independently of being within a `TabContainer`, it was just completely missing this. 

--- KoBeWi:
> TabBar now properly respects its maximum size

But it doesn't seem to grow, like Label?

https://github.com/user-attachments/assets/b45d4f0a-eef1-4fb0-9a39-88a47104a120



--- StarryWorm:
That would be new behavior, which I guess one could call expected. Will add. 

--- StarryWorm:
Added the `TaskBar` behavior for expanding until maximum size whilst taking into account space for left/right buttons. 

--- KoBeWi:
Something is wrong

https://github.com/user-attachments/assets/8bd03eb3-f3df-434f-b415-51d882f08509



--- StarryWorm:
That was a tiny oversight, fixed. The fix also makes it so that it won't constantly resize if going between tabs of varying width, where not all can fit in the space at once.

--- StarryWorm:
Changelog:
* Introduced `Control::get_bound_minimum_size()` which returns the "true" minimum size of the `Control`. 
  * This brings back the behavior that `Control::get_combined_minimum_size()` was responsible for in earlier versions of the PR, but which was removed due to causing update suppression.
  * I updated everywhere appropriate in `scene/`, but did not update any code in `editor/`. Since this is a new feature, none of the editors use it. Doing the change would come with 0 risk but also provide 0 benefit, thus I decided not to, in order to avoid making the PR even noisier. Let me know if I should change it where appropriate. 
* Fixed issues in `TabContainer` relating to the pop-up button in the top bar.
* Fixed issue in `GridContainer` where the 2nd ... nth child in the last row would be improperly squished. 

--- StarryWorm:
Huh... Can you give me the exact setup you used to produce that? When I try it, it works just fine...

max size too small
<img width="338" height="312" alt="image" src="https://github.com/user-attachments/assets/cc0b073a-a190-4588-a0d4-2dd044bdd41c" />

max size large enough
<img width="395" height="306" alt="image" src="https://github.com/user-attachments/assets/fcfafecc-46af-4275-a1ac-a66d4f8db4bd" />



--- KoBeWi:
The maximum size has to be bigger than the current size.

https://github.com/user-attachments/assets/f3eb3a90-33fc-444c-a8ad-15e85b312b8a



--- StarryWorm:
Max size has to be much bigger for the issue to occur... If you set it just large enough (or a bit larger) than needed for it to fit, it will. Otherwise, it will do what you see... Will fix.

--- StarryWorm:
Changelog:
* Added documentation pointing to `get_bound_minimum_size()` in `custom_maximum_size` and `_get_maximum_size()`
* Removed unnecessary change in `grid_map_editor_plugin.cpp`
* Fixed `TabContainer` again. Now works with every maximum size, be it too small, just right, or too large.
  * Yes, it seems hacky, but it was the cleanest way I found to preserve old behavior and enable new behavior without doing a lot of changes that may ripple in ways my testing wouldn't catch.

--- StarryWorm:
Alright, I will look into those and fix them.

--- StarryWorm:
Changelog:
* Rebased
* Fixed an issue where shrink size flags combined with expand would result in filling behavior. This was actually first reported by @AdriaandeJongh [here](https://github.com/godotengine/godot/pull/116640#pullrequestreview-3871875734), but I didn't pay attention to it at the time.
  * New behavior where the expand flag forces the control to its maximum size (if defined) with shrink flags is retained
  * This fixes the Drag and Drop issue highlighted in @Calinou 's review. 

Review: 
* I was unable to reproduce the Control Gallery and Regex `TextEdit` issues. When I opened the projects in 4.7.dev3, master, and the PR branch (after rebase; I did not test before since I needed to), all the `TextEdit` texts aligned to the pixel level. 
<img width="1438" height="633" alt="image" src="https://github.com/user-attachments/assets/87386149-6cd3-402c-be44-bb52a7cc1bfc" />

* For pseudolocalization, the button with the issue is the child of a `VBoxContainer`, which used to not have the [`size_expand` flag](https://docs.godotengine.org/en/stable/classes/class_control.html#enum-control-sizeflags) available in the horizontal dimension, yet somehow the scene file had its `size_flags_horizontal = 6` meaning it was turned on. As such, it behaves as one would expect, expanding to fill the space. The diff below shows this, and when I turn it off it looks as it currently does (with `size_flags_horizontal = 4`)
<img width="622" height="110" alt="image" src="https://github.com/user-attachments/assets/3791d350-145d-493c-a052-c4f7d10ed6b6" />
<img width="524" height="265" alt="image" src="https://github.com/user-attachments/assets/c9ce239c-e067-4f06-8dda-cbf6e583bd01" />

--- StarryWorm:
Changelog: 
* Fixed CI error (related issue: https://github.com/godotengine/godot/pull/118126)
* Rebased

Remaining CI error is unrelated (also fixed in #118126)

--- kitbdev:
- The TextEdit change sounds like https://github.com/godotengine/godot/pull/117154 , its intentional. It looks like the PR wasn't rebased with it when the after screenshots were taken.

--- KoBeWi:
> It will be useful for https://github.com/godotengine/godot/pull/113051. I did some cursory test already and the maximum size fixes one of the problems in that PR.

So I've been trying to update that PR on top of this one and in the end it does not work properly xd
Like, the container (which contains TabBar and `⋮` button) is set as Expand Shrink Center here, the TabBar has minimum size.
<img width="1420" height="93" alt="image" src="https://github.com/user-attachments/assets/0f56fbc0-19a9-498c-a651-106a40007f73" />
Why does it end up shifted so much? (also, if you look closely, the menu button is inside Script...)

I tried different setups and they are all broken. I want the container to be at the center and expand to some specified maximum size, so that TabBar and the menu button are next to each other. You can test it out on this branch:
https://github.com/KoBeWi/godot/tree/maximum_mains
Note that maximum size of the screen tab bar is not enabled, I was testing out stuff using EditorDebugger addon.

Maybe it's not exactly related, but I was waiting for this PR to unblock my work and it turns out it doesn't really help :/ idk if it's a problem with this PR (was it working before? I don't remember, my previous test was just hacking around), or if I'm doing something wrong.

--- StarryWorm:
I'll take a look

--- StarryWorm:
Update: it's not a problem with this PR and thus will not be handled by this PR (i.e. it is ready for review and merge). 
The issue is that the editor pretty much overwrites most native container behaviors so things get messy... Still helping KoBeWi with it, but yeah, not a blocker here.

--- StarryWorm:
Changelog:
* Fixed the BoxContainer bug
  * It was a regression caused [here](https://github.com/godotengine/godot/compare/feeac23a1657c3a54ea72f76d94778b0455e074c..7f447e54f5973ff35bebfcf498c9c3e49b41806b#diff-924c1044ccc7e0fdf6c8d29003f199f962ba1ada43ba8160846b55946468bdecR117-R119) by one of the previous fixes that flew under the radar
* Improved SplitContainer handling
  * This, in my opinion, still results in some somewhat unexpected behaviors, in particular with regard to adding a child with a max size to a SplitContainer whose children (most) all have max sizes, and the container doesn't. "Fixing" this behavior causes a ton of tests to fail, and thus changing this behavior falls outside the scope of this PR.

Review Notes:
* I was unable to recreate the infinite loop after the bugfix. I didn't try beforehand since I wanted to fix what I knew how to fix first, so I can't 100% confirm it fixed it, but it wasn't reproducible on my machine after the fix.

--- StarryWorm:
Changelog:
* Rebased onto #118232 for regression guarding
  * This can be undone before merge, just let me know
* Fixed the `SplitContainer` implementation
* Removed changes to `BoxContainer` and `Container::fit_child_in_rect()` which changed the functionality of the `SIZE_EXPAND` size flag
  * A new `SIZE_MAXIMIZE` size flag is being worked on, which will accomplish what the modified `SIZE_EXPAND` flag did and more, but that will be the subject of a follow-up PR, unless the maintainers prefer it here. Preview changes on [this branch](https://github.com/StarryWorm/godot/tree/size-maximize). 
* Removed unnecessary `maximum_size_updated` hook in `ScrollContainer`

Notes:
* Once the changes are final, I will work on adding test coverage. Those tests can be added either in this PR or a follow-up PR, depending on time constraints for getting new features in the 4.7 dev cycle. 

--- pippenpaddleopsicopolis:
What should be the expected behavior when this property (let's say y = 128) is used on a text edit with scroll_fit_content_height enabled. Currently the typed text disappears once the size of 128 is reached. I'm just making sure this is wanted.

--- StarryWorm:
That `TextEdit` behavior states in its description that "**TextEdit** will [...] fit minimum height to the number of visible lines." Since maximum size takes priority over minimum size, this results in text clipping (the same is true for maximum width and the relevant `scroll_fit_content_width` property).
The way I see it, this is the "expected" behavior.

The behavior could be improved such that the `scroll_fit_content_*` properties only apply up to the maximum size if one is defined (similarly to `ScrollContainer`'s new `SCROLL_MODE_MAXIMIZE_FIRST`).

Since the PR has already been approved with its existing content changes, I am hesitant to add content beyond what the reviewers have approved. @AdriaandeJongh @KoBeWi @bruvzg opinions?
At worst, I'll open a follow-up PR, like I am doing for the `SIZE_MAXIMIZE` flag. 

--- KoBeWi:
Yeah it's better for a follow-up

--- StarryWorm:
Changelog:
* Removed the tests since they aren't for changes made by this PR, they were solely there as regression guards.

PR is now fully ready for merge :)

--- Repiteo:
Thanks!


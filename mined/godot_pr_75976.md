# PR 75976 [CLOSED] — Add "Grid Xy/Yz Plane" toggles to the 3D preview
AUTHOR: qaptoR

## BODY
adds 2 View Menu toggle buttons to en-/dis-able the xy and yz view grids

also adds keyboard shortcuts for fast toggle operations
Grid Xy Plane: with shortcut 'ctrl + ['
Grid Yz Plane: with shortcut 'ctrl + ]'

![image](https://user-images.githubusercontent.com/40372043/231453541-459f3475-8625-492d-bbad-3d2b48c5d105.png)
EDIT: Image updated with proper shortcuts

See proposal for initial details: https://github.com/godotengine/godot-proposals/issues/4128


_Production edit: Closes https://github.com/godotengine/godot-proposals/issues/4128_

## COMMENTS
--- jcostello:
> also adds keyboard shortcuts for fast toggle operations Grid Xy Plane: with shortcut 'ctrl + [' Grid Yz Plane: with shortcut 'ctrl + ]'
> 

The image show the shorcut for both toggles are Ctrl+BracketLeft is that correct?


--- qaptoR:
🤦‍♂️ 
Yup, you're right. My apologies. I used Copilot to duplicate the `yz` line of code, and I do check everything it writes for accuracy, but I also have slight dyslexia, which makes for a lot of well written code with minor grammar mistakes.

I appreciate someone catching that so quickly

EDIT: Also, just ignore the first force push after this comment. It wasn't until after I did it that I remembered to run clang format on the source code... or to do it on all the files, dear me I am really scatterbrained atm

--- qaptoR:
> If the XY/XZ options do nothing when View Grid is unchecked, I suggest disabling them when View Grid is unchecked.

![image](https://user-images.githubusercontent.com/40372043/231483014-56ed8654-e5f8-43b9-a7fd-aa03207483ae.png)
I have implemented that functionality.

EDIT:
I was mostly focused on adding it quickly
so, I added it to the bottom of this function `_toggle_view_grid_plane_options`
![image](https://user-images.githubusercontent.com/40372043/231485765-3f4835b0-79b6-4b7e-b8f0-9c52a80187b1.png)

which is shared by the three switch cases:
![image](https://user-images.githubusercontent.com/40372043/231485864-8ee6e26a-0dd6-42cb-a4b7-5f68a03cd336.png)


but I obviously have to do an `if` check inside the function.

I just realized that the boolean `p_grid_plane_option` is passed by reference, so while it would be using the side-effect of the value being changed inside the function, I could actually remove the disabling out into the switch case, since it will be the correct value there after the function call.

Thoughts?

EDIT: 
it essentially becomes this
![image](https://user-images.githubusercontent.com/40372043/231488503-da0d219f-c2e4-48e1-80ba-8499311d01a6.png)

there's no reason for it to logically not work, and performance-wise it's absolutely no reason to consider the change, it's just a more clean approach. It's also tested and works exactly the same.


--- fracteed:
@qaptoR I just tried a build and appreciate what you are trying to do with this. I do think it would be better to just have the xy and yz grids automatically show up when you go into front or side orthographic modes. The xy/yz grids would then disappear when you go back to perspective view.

While your patch is an improvement, it is still a clunky workflow if you are constantly going back and forth between side/front ortho views and perspective views and having to hit another hotkey every time. It is standard for a 3d package to automatically display the correct grid, depending on the ortho view. Personally I always have grids on in ortho view in any 3d package.

Maybe some users also use the xy and yz grids in the perspective views? This can be useful if you are modelling and snapping to a workplane, but is most likely not common usage in a game engine.

--- Calinou:
> Maybe some users also use the xy and yz grids in the perspective views? This can be useful if you are modelling and snapping to a workplane, but is most likely not common usage in a game engine.

The main use case where you want XY/XZ grids in perspective view is for 2.5D sidescrolling games.

Other than that, I agree we should toggle the XY/XZ grids automatically based on the current view preset when using orthogonal mode.

--- qaptoR:
What if the toggle was for 'per view mode', so you can toggle it on for orthogonal and off for perspective

The reason I originally created this PR for my own needs was because I didn't always want the Grid in orthogonal mode as it felt claustrophobic unless I actually needed to measure something.

And for Perspective mode, I was working on a tutorial about spatial transformations and I needed the Grids to help show the changes in different axes, but only at specific moments in the tutorial after each example.

I also use it quite a bit when I'm creating 'prefab' scenes, since they're all centered about the origin. I will admit I might be an edge case but I generally work in perspective when aligning things. Although, I will admit that the view grid is not ideal when doing it further away from the origin, and I have been pondering about a measuring tool for perspective mode that adapts to the current work area.

--- fracteed:
@qaptoR I had a look at how some of the popular 3d packages are doing this for reference. Blender has a separate checkbox for floor and grid. The grid option toggles for all ortho views only. The floor option is only for the floor grid in non-ortho views. (note that the axis in the screenshot has nothing to do with the grids)

![grid](https://user-images.githubusercontent.com/7741669/231939782-b9624fbf-489b-4a81-a936-1156371a82d5.jpg)

Houdini and Cinema 4d both have just a grid toggle, which toggles it on or off in ortho or non-ortho views. I personally believe this is the best approach. Separating it like blender does, is more cluttered in the ui and doesn't really serve a purpose since the floor grid toggle does nothing in ortho views and the grid option does nothing in non-ortho views (as can be seen in this screenshot, it is greyed out in perspective view).

Just one grid toggle should work in any view. I don't think that there should be separate xy/yz/zy toggles as there currently are in Godot.

I agree with you that there are times when it can be very useful to see grids in the 3d view but I think it should be a separate feature (which is obviously outside the scope of this PR). This concept is usually called a workplane or construction plane in 3d dcc packages. It is a temporary grid in non-ortho views that can be snapped, moved of scaled on any arbitrary axis. This can then be used to snap and align objects to. 

Blender doesn't have one built in (like Modo or Houdini do) but you can see from this addon what I am talking about. https://github.com/BenjaminSauder/Workplane

Personally, I think that just having the xy/yx options in the perspective viewport is very much a corner case if they can't be moved to other locations off the 0 axis. Unless you are doing a 2.5 platformer that doesn't have any parallax layers and has everything on the z = 0 point. 

--- qaptoR:
I think you're right, this PR while useful to me in spirit, does not address the underlying needs I have.

Should I close this PR for the time being? Or re-orient this PR to align with the new goals?

What I hear needs being done:
- automatically set xy/yz view grid based on current orthogonal view
- `view grid` already has a keybind so nothing is needing done there

--- fracteed:
@qaptoR yes, I think it would probably be best to close this PR down and open another to add the basic toggle grid functionality to ortho views. This is a much-needed functionality that would make in consistent with other 3d packages. Currently when changing to 4 way split view, the "view grid" option only toggles the top view, whereas "view origin" toggles it in all 4 views.

There is already a "view grid" menu option, so the expected behavior would be that this toggles just the floor grid in non-ortho views (as it currently does) as well as grids in all ortho views.

I still think that the construction plane idea would be very useful, but it is not exactly a trivial job and would need a solid design proposal first.


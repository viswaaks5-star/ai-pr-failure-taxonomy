# PR 114806 [MERGED] — Fix OptionButton PopupMenu not shrinking after item changes
AUTHOR: Clubhouse1661

## BODY
Fixes #114786.

Updates `OptionButton::show_popup()` to correctly handle `PopupMenu` resizing when content changes from larger to smaller items.


- Calls `popup->set_min_size(Size2(0, 0))` before opening. This is crucial because `Window::popup(rect)` clamps the size to the current `min_size`. Without resetting it, the window refuses to shrink to the new smaller content size because it's still constrained by the previous items' minimum size.
- Explicitly enables `popup->set_shrink_height(true)` to ensure the height is recalculated to fit the new content.


Verified with the MRP from the issue. The PopupMenu now immediately shrinks to the correct size when switching from long items to short items.


https://github.com/user-attachments/assets/631e104e-4a17-43d5-a56d-dc0827b7121c


https://github.com/user-attachments/assets/5a365820-04c9-49ae-b225-e186a5927908




## COMMENTS
--- AThousandShips:
Please turn off the copilot feature for contributing to Godot, it creates a lot of noise (and uses CI resources) and risks including bad suggestions that you then have to fix because it didn't understand how we write code and do things in the engine

--- akien-mga:
See also https://github.com/godotengine/godot/pull/114760.

CC @bruvzg @YeldhamDev 

--- Clubhouse1661:
Understood, I've disabled the Copilot auto-review feature.

--- YeldhamDev:
@akien-mga This PR doesn't affect the bug I fixed, because it doesn't use an `OptionButton`. :wink:

In my PR however, I moved `popup->set_shrink_width(false)` line to the constructor, as it doesn't make sense to set it every time it pops up. The same could be done here instead.

--- Clubhouse1661:
Agreed. Updated to follow @YeldhamDev's suggestion from #114760: 

Moved `popup->set_shrink_width(false)` from `show_popup()` to the constructor since it's a one-time property

--- YeldhamDev:
`popup->set_shrink_height(true)` should follow suit (unless the fix needs it to be called every popup).

--- bruvzg:
> `popup->set_shrink_height(true)`

This is default, so not needed at all.

--- Clubhouse1661:
That's right. Removed `set_shrink_height(true)` as it's the default. 
The fix now only adds `set_min_size(Size2(0, 0))` in `show_popup()`, which is a cleaner fix. 
Tested with the MRP, and it works correctly.

--- scgm0:
I believe the actual fix should be to remove `popup->set_shrink_width(false)` rather than manually calling `popup->set_min_size(Size2(0, 0))`. When `shrink_width` is `true`, `PopupMenu` automatically shrinks its width in `_pre_popup()`. 
So why was `popup->set_shrink_width(false)` added in the first place?(https://github.com/godotengine/godot/pull/114438)
@bruvzg 

--- bruvzg:
> So why was popup->set_shrink_width(false) added in the first place?

Because, it should not shrink width to anything smaller than the size of the `OptionButton` only expand.

--- bruvzg:
For 4.7 we probably should revert #104399, #112604 and #114438 and fully reconsider how popup auto sizing works.

--- scgm0:
> For 4.7 we probably should revert #104399, #112604 and #114438 and fully reconsider how popup auto sizing works.

Perhaps we could have `_pre_popup()` accept the `screen_rect` from `popup(const Rect2i &p_screen_rect)`, and if `screen_rect` is valid, use `screen_rect.size` instead of `0` to adjust the size?


--- Clubhouse1661:
Currently it looks like sizing responsibilities are split between Window, PopupMenu, and individual widgets.

If we're considering a full redesign for 4.7, we could introduce a `PopupConstraints` class which includes all sizing behavior in a single structure, and be called via a new method like `popup_with_constraints()`

--- akien-mga:
Thanks! And congrats for your first merged Godot contribution :tada:


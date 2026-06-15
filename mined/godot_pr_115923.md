# PR 115923 [MERGED] — Core: Fix ClassDB class list sorting regression
AUTHOR: GusatuDamianAlexandru

## BODY
Fixes #115914

Regression in 4.6 where ClassDB::get_class_list() and ClassDB::get_extensions_class_list()
no longer return an alphabetically sorted list, as they did in 4.5.1.

This restores the intended alphabetical ordering by using StringName::AlphCompare for
the SortArray comparator.

Testing: Built editor (linuxbsd) and ran the reproduction script from the issue; got "Sorted? True".

No functional changes beyond restoring deterministic sort order.

<img width="1162" height="675" alt="Screenshot 2026-02-05 224306" src="https://github.com/user-attachments/assets/60c0d8ec-a2b6-4550-8b87-ff91174ab9b5" />


## COMMENTS
--- akien-mga:
Please don't use Copilot for reviews, this is just noise and not providing anything helpful to human reviewers.

--- GusatuDamianAlexandru:
Sorry about that. I didn’t realize Copilot code review would post automatically. I’ve disabled it and won’t use Copilot reviews on Godot PRs going forward.


--- GusatuDamianAlexandru:
Thanks for the review! Yep, AlphCompare was the missing piece. Happy to see it cherry-picked to 4.6.x if needed.

--- jloehr:
Thanks for your PR. Would've created one myself today otherwise.
Looking at #108577, it seems `ScriptServer::get_global_class_list` is also missing the AlphCompare in its `SortArray`. Maybe we want to fix that regression as well?

Would love to see this in a 4.6 minor, as it is a breaking behavior for us.

--- mihe:
As talked about in #115914, this also restores the determinism of `.godot/global_script_class_cache.cfg`, so that you actually get the same output on every launch/export, which otherwise caused problems for the [delta patching](https://github.com/godotengine/godot/pull/112011) with certain use-cases.

--- Repiteo:
Thanks! Congratulations on your first merged contribution! 🎉 

--- Repiteo:
Cherry-picked for 4.6.1.


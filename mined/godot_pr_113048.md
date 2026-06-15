# PR 113048 [CLOSED] — Fix crash in `SceneTreeDock` by pre-creating nodes for replacement
AUTHOR: wheatear-dev

## BODY
<!--
Please target the `master` branch in priority.

Relevant fixes are cherry-picked for stable branches as needed by maintainers.

To speed up the contribution process and avoid CI errors, please set up pre-commit hooks locally:
https://contributing.godotengine.org/en/latest/engine/guidelines/code_style.html
-->

Fixes #113018.

During a (root) `Node` replacement event such as changing its type in the UI, the old and new nodes are created and then immediately provided to `SceneTreeDock::replace_node`, at which point they may not have initialized fully.

This PR separates this single action into two steps:

1. Eagerly build _all_ old and new nodes from `selection`, into a `Vector<Node *>` for each
2. Iterate through `old_nodes` and `new_nodes`, calling `SceneTreeDock::replace_node` on each pair
## Before

Changing the node type, and saving the scene each time, would crash the editor after not many iterations.

https://github.com/user-attachments/assets/475bc6a3-6a4b-4097-9a25-006e7db827db

Sorry for the low resolution (480p), GitHub is limiting video uploads to 10MB today.


## After

I manually changed node type at least 20 times, saving the scene each time. No crash at all.

Video evidence of 100 successful re-types is [here, on YouTube](https://www.youtube.com/watch?v=nMqvV5Sdc8w). Way too long for 10MB.

## Testing

Okay attached is my MacOS-only, ChatGPT-created, terrible test-harness!

It fails with normally single digit iterations for `master`.
[Test113048.zip](https://github.com/user-attachments/files/23691541/Test113048.zip), 
[with minimal reproduction project ](https://github.com/user-attachments/files/23691611/issue-113018-2.zip)



## COMMENTS
--- wheatear-dev:
Having spoken to @migueldeicaza , this is unit testable using Doctest.

I'll look tonight, after work.

--- lyuma:
This is not a complete fix. See my comment here
https://github.com/godotengine/godot/issues/113018#issuecomment-3601328063

The underlying cause is changing the top selected nodes in SceneTreeDock::_create from `List<>` to `List<>&`

--- wheatear-dev:
This is fixed better by #111837 . Closing 😌 


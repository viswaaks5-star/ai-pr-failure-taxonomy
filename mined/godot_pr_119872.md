# PR 119872 [MERGED] — Fix Polygon2D being culled against a stale AABB after editing vertices
AUTHOR: Ijtihed

## BODY
<!--
Please target the `master` branch. We will take care of backporting relevant fixes to older versions.

Before submitting, please read our checklist for contributors:
https://contributing.godotengine.org/en/latest/engine/introduction.html#checklist-for-new-contributors

Use of AI must be disclosed and should include a description of how it was used.
-->

## What problem(s) does this PR solve?

- Closes #119843

## Additional information

The Polygon2D draw fast path added in #117334 updates the vertex buffer in place with `mesh_surface_update_vertex_region()` when the vertex count does not change but it never refreshess the mesh surface AABB

Canvas culling uses the mesh AABB from `mesh_get_aabb()` for the item's cull rect so after moving points with the polygon editor move tool, the node keeps being culled against its old bounds and disappears once those bounds leave the view. Reopening the scene works around this until the polygon is moved again, since that forces a full `mesh_add_surface()` path.

This refreshes the AABB after the surface update. Skeleton-deformed polygons always take the `needs_clear` path and compute their AABB from bone data so their AABB is left untouched.

### Before

<img width="1936" height="1048" alt="editor_buggy" src="https://github.com/user-attachments/assets/47ee7957-f720-4ab6-8c63-a9adf3f15a0a" />

### After

<img width="1936" height="1048" alt="editor_fixed" src="https://github.com/user-attachments/assets/550f553e-cd71-4abe-8e36-0aa67836d97f" />

I tested it with the MRP from the issue. The full test suite with `--test` passes and skeleton-skinned polygons render identically from my end in both before and after.

AI use disclosure: ChatGPT was used to help draft and edit this PR description to match the requirements.


## COMMENTS
--- AThousandShips:
> ChatGPT was used to help draft and edit this PR description to match the requirements.

Please do not use AI tools to write PR descriptions

--- Ijtihed:
> > ChatGPT was used to help draft and edit this PR description to match the requirements.
> 
> Please do not use AI tools to write PR descriptions

Okay, noted, sorry! 

--- Repiteo:
Thanks! Congratulations on your first merged contribution! 🎉 


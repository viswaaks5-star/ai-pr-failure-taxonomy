# PR 119206 [CLOSED] — Improve circular references handling
AUTHOR: ringerc

## BODY
# Improve handling of circular references in scene loading

While the PackedScene loading crash when circular references from https://github.com/godotengine/godot/issues/24146 is fixed, the user experience when circular references exist in a project remains confusing and difficult.

When two scenes reference each other via `@export var scene: PackedScene` (e.g., Scene A → Scene B → Scene A), Godot previously showed confusing error messages like "non-existent resource" or cryptic "Busy" errors. It displays a dialog that complains that the scenes could not be found, with a list of sub-resources referenced by each scene, but no explanation for why these scenes (which do in fact exist) could not be found, or that the underlying issue was really a loading error caused by a circular reference.

This PR improves the user experience by:

- Clearly identifying cyclic references in both console output and the editor dialog
- Providing actionable guidance on how to fix affected scenes
- Showing line numbers to help locate problematic references
- Suggesting prevention strategies for PackedScene cycles

I was prompted to raise this after spending some time manually repairing a project for someone I was helping with Godot as they were completely stuck after creating a scene where one portal in a level scene could take the player back to a prior level (with level links specified using `@export var to_load : PackedScene`. That's not the right way to implement that pattern, but the author didn't know that, it's a pattern shown in various (3rd party) guides, and Godot broke pretty badly when they did it.

## Test

With the same test case as attached to https://github.com/godotengine/godot/issues/24146#issuecomment-4367331978 when I open it in a patched build I now see:

<img width="500" height="503" alt="image" src="https://github.com/user-attachments/assets/873f5805-2f1c-44e2-9b2f-706ec70b279b" />


and logs are

```
➜  godot-engine git:(improve-circular-references-handling) ✗ Vulkan 1.4.312 - Forward+ - Using Device #1: NVIDIA - NVIDIA RTX PRO 2000 Blackwell Generation Laptop GPU

ERROR: Cyclic resource reference detected. [Resource file res://circular2.tscn:8]
   at: _parse_node_tag (scene/resources/resource_format_text.cpp:297)
ERROR: Failed loading resource: res://circular2.tscn.
   at: _load (core/io/resource_loader.cpp:317)
ERROR: Cyclic resource reference detected. [Resource file res://circular1.tscn:8]
   at: _parse_node_tag (scene/resources/resource_format_text.cpp:297)
ERROR: Failed loading resource: res://circular1.tscn.
   at: _load (core/io/resource_loader.cpp:317)
```

## Changes

(LLM-assisted)

**Console error messages:**
- Changed "referenced non-existent resource" to "cyclic reference while loading" when `ERR_BUSY` is detected
- Changed generic "Busy" parse error to "Cyclic resource reference detected"

**Dependency error dialog:**
- Dialog now shows "Load failed due to cyclic references:" instead of "missing dependencies" when cycles are detected
- Uses warning icon instead of failure icon for cyclic items
- Shows "Cyclic reference with \<path\>" instead of "Referenced by \<path\>"
- Displays line numbers from the .tscn file (e.g., "res://scene2.tscn (line 3)")

**Recovery hints:**
- Added a hint panel with step-by-step instructions to fix cyclic references using a placeholder scene
- For PackedScene cycles specifically, suggests using `@export_file("*.tscn")` with dynamic loading

## Notes

This PR does not prevent cyclic references from being created. Save-time detection would require dependency analysis of external resources, which I thought was going to be too intrusive and possibly risky. 

Instead, it focuses on helping users understand and recover from the situation when it occurs.

Since #97912, `@export_file` paths auto-update when files are moved, making the suggested workaround (`@export_file("*.tscn")` with dynamic loading) more practical.

## COMMENTS
--- KoBeWi:
If the dialog is able to detect circular references, it could also allow to fix them. You could just remove one of the problematic dependencies.

--- ringerc:
@KoBeWi Good point - it could just set one to null.

It'd mean the user wouldn't have performed that action themselves, and would have to manually fix it, but it could display an explanation I guess. Worth a try.

I should also look at whether I can improve behaviour when running a project containing a reference loop before it is saved and loaded. Currently execution will crash claiming that a field that is visibly non-null is null (because loading failed due to circular reference).

--- ringerc:
I was a bit uncertain about how feasible your suggestion was @KoBeWi, and had some concerns about whether it was appropriate to modify the user's code directly. It seems to me that it could be more confusing than the status quo to have a somewhat unpredictable value that was previously non-null set to null or erased. Especially if the autofix can't easily open the modified file or UI element and highlight the change in a clear and obvious manner.

I'd be particularly concerned when the user isn't using git. Git use is is surprisingly awkward with Godot due to lack of built-in support and Godot's requirement that the git plugin be part of the project itself, duplicated for each project and mixed up with the project's real sources. It's going to be less common, and modifying user files automatically when there's no guarantee of revision control is a risk I'm not keen on.

I threw this suggestion at an LLM tool to scope it anyway, as I don't yet have the experience with the Godot codebase to do a decent job of that myself. I didn't express any preference for solution, only suggested an evaluation for feasbility.

The tool's output seems to align with my gut feeling. ~~Though I need to look into the claim about ext_resource being unable to be nil a bit more - since at script-level, a state exists where an external resource is not yet assigned any value when added to a scene.~~ Edit: Corrected, and content below updated.

See output below:

---

> [!NOTE]
> **Edited:** the original version of this comment claimed `[ext_resource]` couldn't be "nulled" and proposed a placeholder-redirect fix. That framing was wrong — the tscn format does have a meaningful "no override" state (just omit the property assignment line), and a "restore default" autofix is both feasible and a better fit than redirecting to a placeholder. Sections below are updated; struck-through text is what was originally posted.

# Evaluation: KoBeWi's "fix-the-cycle" suggestion

## Verdict
**Feasible but with significant caveats.** The mechanical fix is easy; making it safe and useful for the user is the harder part. Worth doing as a **consent-gated button**, not a silent auto-fix.

## What's already in place
- `ResourceLoader::rename_dependencies(owner_path, {{old, new}})` already rewrites `[ext_resource]` paths in `.tscn`/`.tres` files. The dialog's existing "Search" button (`editor/file_system/dependency_editor.cpp:1052`) uses this.
- The PR already tracks the offending `[ext_resource]` line number per missing dep (`missing_to_owners` keys carry `path::type::line`).
- `p_report` gives us the cycle pairs directly.

~~So the core mechanical operation is **one line**: call `rename_dependencies` to swap one cyclic edge to a placeholder.~~

**Correction:** the existing `rename_dependencies` only rewrites `[ext_resource]` *paths*. To actually break a cycle by restoring a property to its default, we need to remove both the `[ext_resource]` header line and every node-property assignment that references its id. That's new code — see "Implementation paths" below.

## What's actually hard

### 1. ~~There's no "null" for an `ext_resource`~~ Restoring "default" state is real, but needs a coupled edit

Property overrides in a `[node]` block are written as `assign = value` lines (`scene/resources/resource_format_text.cpp:308-316`). If a property's line **isn't present** in the .tscn, no override exists for that node and the script's declared default applies — null for `@export var foo: PackedScene` with no initializer, or whatever the script set otherwise. That's a perfectly valid "no value assigned" state, exactly as it would be for a fresh `@export` the user just added.

The catch is that you can't break a cycle by editing only one side of the file:

- The `[ext_resource]` header itself requires a `path` (`scene/resources/resource_format_text.cpp:473-492`), and the loader **eagerly** loads every declared ext_resource at parse time via `ResourceLoader::_load_start` (`resource_format_text.cpp:527`) — even if no node references it. So removing just the property assignment doesn't help; the cyclic load still fires.
- Removing only the `[ext_resource]` line while leaving `foo = ExtResource("1_xxx")` makes `_parse_ext_resource` return `ERR_PARSE_ERROR` ("Can't load cached ext-resource id") at line 139, failing the whole file.

So the autofix has to be **a coupled edit**: strip the `[ext_resource]` line *and* every `<prop> = ExtResource("<id>")` line that references its id. Result: the affected property reverts to the script-declared default, exactly as if the user had never assigned anything. That's the right semantics — much better than the placeholder redirect I originally suggested, which would silently point the property at the wrong scene.

### 2. ~~The fix replaces a load failure with a logic bug~~ The "restore default" outcome is well-defined
With placeholder redirect, the property would silently point at a placeholder scene, creating a hidden logic bug. With "restore default" (strip the override), the property is null (or whatever the script defaults to) — same state a fresh `@export` would have. The user still has work to do (decide how the reference *should* be expressed), but the broken state is no longer hiding behind a misleading value.

The dialog should still clearly tell the user what changed and why.

### 3. Picking which edge to break is non-obvious
The PR's detection only finds direct A↔B 2-cycles (`p_report.has(missing_path)` + reverse check). For a 3+ length cycle (A→B→C→A) it won't fire at all. Even for a 2-cycle, "break the A→B edge" vs. "break the B→A edge" is arbitrary — both files are listed as cyclic.

You'd need to either:
- Let the user click the specific edge to break (more clicks, but explicit), or
- Pick one heuristically (e.g. the file the user was loading → break its outgoing edge first), and document the choice.

The first matches Godot's existing dependency-editor philosophy (manual, deliberate). Recommended.

### 4. Generalizing beyond PackedScene
The PR specifically calls out PackedScene cycles. The "restore default" approach is actually *more* general than the placeholder approach was — it works for any cycled type, since it removes the override rather than redirecting it. Practically still gate to PackedScene cycles in v1 to limit scope, but the mechanism extends naturally.

### 5. "Open the modified file to the relevant path" is the weakest part
Two interpretations:

- **Open the scene in the scene editor and select the affected node.** Most useful, but we don't currently know which node owns the offending property — only the line number of the `[ext_resource]` line. Mapping back from `ext_resource id` to the node that assigns it would require parsing node tags during fix (which the restore-default rewrite has to do anyway, since it needs to find and strip those property lines — so this comes essentially for free).
- **Open the .tscn as text in the script editor at line N.** Mechanically possible (`ScriptEditor::edit(res, line, col)` exists at `editor/script/script_editor_plugin.cpp:2197`), but PackedScene isn't a registered text-editor resource type, and editing tscn-as-text is not an end-user idiom in Godot. Feels developer-y and somewhat off-brand for the editor.

Since the rewrite step already walks node tags to strip property assignments, it can record which nodes were affected and pass them up to the dialog. The dialog can then load the scene (now loadable) and select the affected node(s) in the scene tree — much more useful than opening as text.

## Implementation paths

Two reasonable shapes for the rewrite:

1. **Line-level rewrite** of the .tscn. Pass 1: find the `[ext_resource]` line for the cyclic dep, capture its `id`. Pass 2: rewrite the file omitting that ext_resource line and any `<prop> = ExtResource("<id>")` lines under `[node]` blocks. Minimal diff, easy for users to review in VCS — directly addresses the "no-VCS user" concern. Best fit for this PR's text-only scope.

2. **Round-trip via `SceneState`**. Load the scene with `abort_on_missing_resources=false`, mutate the SceneState's property/ext-resource lists, resave. Cleaner conceptually and would extend to binary `.scn` automatically. Downside: introduces formatting churn in the saved file (line ordering, whitespace), which is bad in a "we just modified your file" context.

(1) is recommended for v1.

## Edge cases worth checking
- **Same ext_resource referenced from a sub-resource (`[sub_resource]` block) or a resource dictionary**, not only from `[node]` properties. The strip pass needs to walk all assign-lines, not just node ones, or refuse the fix if the ext_resource is referenced outside a node block.
- **UID-only references**. The id is file-local, so this is fine, but worth a unit test.
- **Multiple property assignments to the same id**. Strip them all; don't stop at the first.
- **The cyclic dep used as a node's `instance` field** (i.e. the scene is *instanced* into another scene cyclically, not just held by an `@export`). Removing the instance line would orphan or destroy the node. Different fix needed — probably refuse autofix in this case and tell the user the cycle is structural.

## Other risks
- **No editor undo for file rewrites.** `rename_dependencies` writes via `.depren` rename — VCS recovery only. Need a confirmation step. Worth highlighting given the no-VCS concern raised above.
- **EditorFileSystem cache invalidation.** Existing rewrite flow works for the Search button, so should be fine, but worth verifying the modified file gets re-scanned before the auto-reload.
- **Cycle detection is shallow.** Anything longer than length-2 escapes the heuristic, so the auto-fix simply wouldn't appear for those cases — this is a feature gap, not a hazard.

## Recommended scope if you do it
1. Add a per-edge **"Break this reference"** button in the cycle list (not a single global auto-fix).
2. On click: a confirmation dialog showing (a) the file and line that will be modified, (b) the property name(s) on the node(s) that will be reverted to default, and (c) a clear note that the user should treat this as a starting point for a proper redesign of the reference pattern.
3. Rewrite via the line-level approach (path 1 above): strip the `[ext_resource]` line and matching `<prop> = ExtResource("<id>")` lines.
4. After rewrite: close the error dialog, reload the scene, and select the affected node(s) in the scene tree (the rewrite step already knows which they are).
5. Restrict v1 to PackedScene 2-cycles. Treat longer/typed cycles as out-of-scope.

This stays within the PR's stated philosophy ("help users understand and recover" — not "silently mutate the project") while delivering the usability win KoBeWi is suggesting, and the restored-default outcome is more honest about what's actually broken than the placeholder approach would have been.


--- ringerc:
**TL;DR: I think it might make sense to keep this as-is, as a human-gated deliberate action.**

Perhaps a button could be added beside the edit button with an ❌  or something that clears the reference in an automated edit, as a separate follow-up PR. I'm not convinced it's a good idea though, especially if there's no guarantee the user's files are under version control.

In a large project it could be hard for a user to track down the change and fix it properly. As godot projects frequently lack any sort of test automation they'd often have to manually hit this specific code-path to find the now-undefined reference after the edit.

I'm going to explore a couple of other possible improvements though:

* Detecting cycles earlier, and throwing a better exception, so that cycles hit at runtime cause failures with something like "resource loading failed due to reference cycle" rather than just returning nil; this would be less confusing for users. My current improvement PR doesn't address this, it only tries to solve the related issue at project-loading time.
* Using ^ to then simplify the loading dialog logic

--- ringerc:
Pushed some (hopefully) improvements.

--- hpvb:
I don't think this is reviewable. There's so much text in the various comments that are all entirely AI generated that is at this point no longer possible to ascertain what the intent behind this PR even is.

--- ringerc:
OK. I've been pretty up-front about separating LLM content from my own writing; I've clearly marked boundaries around anything LLM-generated, provided it as context that can be optionally skimmed or ignored.

I take issue with you saying that it's not possible to tell what the intent of the PR is. If you take a look at the [linked issue report](https://github.com/godotengine/godot/issues/24146) from the PR header and my [comment on it](https://github.com/godotengine/godot/issues/24146#issuecomment-4367331978) the problem should be IMO be pretty clear, and the PR description says it seeks to address that by providing a clearer error. Including a screenshot showing the result.

I've also provided a reproducible test case for the problem, screenshots of the behaviour etc; see https://github.com/godotengine/godot/issues/24146#issuecomment-4367331978 .

Complexity grew as I tried to address @KoBeWi 's [comment](https://github.com/godotengine/godot/pull/119206#issuecomment-4370617981) by exploring whether an autofix was feasible - and it doesn't look like it is.

But I also understand not wanting to wade through the details. Fine with me, this was an experiment to see if it was feasible to address the issue. IMO it looks like it is.

If anyone wants to pick up the experiment and clean it up they're welcome.


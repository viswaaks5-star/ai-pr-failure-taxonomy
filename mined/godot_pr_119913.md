# PR 119913 [CLOSED] — Add PhysicsDirectSpaceState3D.intersect_ray_into for allocation-free raycasts
AUTHOR: justin-bobr

## BODY
### Summary

Adds an allocation-free variant of `PhysicsDirectSpaceState3D.intersect_ray()`:

```cpp
bool intersect_ray_into(Ref<PhysicsRayQueryParameters3D> parameters,
                        Ref<PhysicsRayQueryResult3D>     result);
```

with a new `RefCounted` result holder `PhysicsRayQueryResult3D`. The caller pre-allocates the holder once and reuses it across every raycast, avoiding the `Dictionary` + per-key `Variant` boxing the existing `intersect_ray()` performs on every call.

Purely additive — the existing `intersect_ray()` is **unchanged**. No backwards-compat impact on projects, GDScript, GDExtension, or the C# bindings. The new class follows the same shape as `PhysicsTestMotionResult3D` (RefCounted, methods-only, populated by the engine).

```gdscript
var query := PhysicsRayQueryParameters3D.create(from, to)
var result := PhysicsRayQueryResult3D.new()  # allocate once, reuse every frame
var space := get_world_3d().direct_space_state
if space.intersect_ray_into(query, result):
    position = result.get_position()
    normal = result.get_normal()
```

### Why this is worth adding

`intersect_ray()` is in the hot path of many runtime systems where the per-call `Dictionary` allocation becomes a measurable cost:

- **Hitscan weapons** in FPS games (1+ ray per shot, multiple for spread / penetration)
- **Camera collision** (per-frame, per actor)
- **Line-of-sight visibility checks** (fog-of-war, AI sensing)
- **Foot IK probes** (one per foot per frame)
- **Audio occlusion** (one per audible source)
- **Grenade trajectory preview** (per simulation step)

Each call currently allocates:
1. C++ side: one `Dictionary` + 7× `Variant` boxes (`position`, `normal`, `face_index`, `collider_id`, `collider`, `shape`, `rid`) + per-key `StringName` interning.
2. For C# users: a managed `Godot.Collections.Dictionary` wrapper per call, plus **every `result["position"]` read crosses the binding twice** — once to fetch the `Variant`, once to unbox.

For projects where these add up (FPS games, busy AI scenes, twin-stick shooters with hitscan), this becomes a visible item in the GC histogram and a measurable contributor to the frame-time tail. The new path writes straight into the result holder's typed fields and field reads go through the regular PtrCall path used by every other engine getter — no Variant round-trip on either side.

### What changed

| File | Lines | Purpose |
|------|-------|---------|
| `servers/physics_3d/physics_server_3d.h` | +37 | Forward decl + `PhysicsRayQueryResult3D` class + `_intersect_ray_into` declaration |
| `servers/physics_3d/physics_server_3d.cpp` | +50 | `_intersect_ray_into` impl + `PhysicsRayQueryResult3D::_set_result/_clear/_bind_methods` |
| `servers/register_server_types.cpp` | +1 | `GDREGISTER_CLASS(PhysicsRayQueryResult3D)` |
| `doc/classes/PhysicsDirectSpaceState3D.xml` | +18 | New `intersect_ray_into` method doc with GDScript example |
| `doc/classes/PhysicsRayQueryResult3D.xml` | +72 (new) | Full class doc, all 8 getters, usage example |

Total: 178 lines of code + docs. No deletions, no renames.

### API surface

`PhysicsRayQueryResult3D` (new, RefCounted) — methods only, all `const`. Mirrors `PhysicsTestMotionResult3D` style.

| Method | Returns | Notes |
|--------|---------|-------|
| `has_hit()` | `bool` | Same value the call returns |
| `get_position()` | `Vector3` | Intersection point, global coords |
| `get_normal()` | `Vector3` | Surface normal |
| `get_face_index()` | `int` | `-1` unless `ConcavePolygonShape3D` |
| `get_collider()` | `Object` | Colliding node, or `null` on miss |
| `get_collider_id()` | `int` | Instance ID |
| `get_shape()` | `int` | Shape index on the collider |
| `get_rid()` | `RID` | Physics RID of the intersecting object |

On miss the holder is cleared (`has_hit() == false`, other getters return zeroed defaults).

### Bindings & scripting languages

- **GDScript** — works out of the box. `PhysicsRayQueryResult3D.new()` and the getters above.
- **C# / Mono** — auto-generated `Godot.PhysicsRayQueryResult3D` wrapper via the same `GDREGISTER_CLASS` path that handles `PhysicsTestMotionResult3D`. All getters become `GetXxx()` methods. Reads use the existing PtrCall path that powers every other engine getter (no Variant round-trip).
- **GDExtension** — registered via `GDREGISTER_CLASS`, so language bindings (rust-godot, godot-cpp, etc.) pick it up automatically.

### Backwards compatibility

Zero impact on existing projects:

- `intersect_ray()` signature, behavior, and Dictionary key shape — **unchanged**.
- The new class doesn't shadow or replace anything.
- No serialised resource or scene-file format changes.

Existing call sites get no benefit unless they actively opt into the new method. Migration is a small per-call-site change (declare a result field, pass it as the second arg, read typed fields instead of dictionary lookups).

### Performance methodology

The patch was developed against a 16-player competitive FPS project running on the Mono build. Measured impact comes from two places:

1. **Engine-side**: `Dictionary` + 7× `Variant` heap allocation per successful `intersect_ray()`. Eliminated for the new entry point by writing directly into the holder's fields.
2. **C# binding**: `Godot.Collections.Dictionary` managed wrapper + per-property cross-binding `Variant` unboxing. Replaced by the standard PtrCall getters that every other engine class uses.

The reduction is proportional to raycast frequency. On a 60-second listen-server bot match (8 bots, dust2-scale map, full-auto fire) the project-side migration cut the per-second `intersect_ray`-attributable allocations to a small constant.

I'll be happy to add an engine-only microbenchmark to `tests/` if reviewers want a number in-tree before merge — let me know the preferred shape.

### Open questions for reviewers

1. **Naming**: `intersect_ray_into(query, result)` follows the C++ "out parameter" convention. Alternatives considered: `intersect_ray_to`, `intersect_ray_filled`, `cast_ray`. Happy to rename.
2. **Default-init values on miss**: `_clear()` sets `face_index = -1` (matches `RayResult::face_index` default and the existing `intersect_ray` semantics) and other fields to zero defaults. Open to leaving them untouched if reviewers prefer; just need to document either choice clearly.
3. **Member exposure**: I exposed getters only (no `<members>` block, no `ADD_PROPERTY`). Matches `PhysicsTestMotionResult3D`. If reviewers want property-style access from scripts, I can add `ADD_PROPERTY` with empty setters (read-only), though that mixes a bit awkwardly with the editor's property inspector for a holder that should never be edited from there.

### Follow-up work (intentionally not in this PR)

To keep the PR small and reviewable, the following are explicitly **not** included here. Happy to do them as separate PRs if there's appetite:

- **2D equivalent**: `PhysicsRayQueryResult2D` + `PhysicsDirectSpaceState2D.intersect_ray_into`. Same pattern, mechanically applied to the 2D server.
- **Same pattern for the other space-state queries that allocate `Dictionary` / `Array` results**: `intersect_shape`, `intersect_point`, `get_rest_info`, `cast_motion`. These have multi-result shapes that need slightly more design (caller-provided typed array? max-results cap on the holder?), better as a follow-up.

### Testing

- Manual: bot-match scenario above, 60-second sessions before/after with the same query params. Verified equivalent hit results between `intersect_ray` and `intersect_ray_into` (collider, position, normal, face_index match within float-precision).
- Edge cases verified by inspection:
  - Miss case: `has_hit() == false`, all getters return zero/`null`.
  - Repeated calls reusing the same result holder: previous fields cleanly overwritten via `_set_result` / `_clear`.
  - GDScript and C# both pick up the new class in autocomplete + docs.

---

_This is my first upstream Godot contribution — happy to adjust the patch, naming, doc wording, or anything else the reviewers prefer. If a `godot-proposals` issue is expected first for this kind of additive API, let me know and I'll open one and link it back._


## COMMENTS
--- AThousandShips:
Your commit seems not to be linked to your GitHub account. See: [Why are my commits linked to the wrong user?](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/troubleshooting-commits/why-are-my-commits-linked-to-the-wrong-user) for more info. (It's also a seemingly unrelated account with a different name, why is that?)

Did you use any AI tools to write the PR description, or write any part of the PR code? If so that needs to [be disclosed](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions) and we do not accept PR descriptions written in this way

--- justin-bobr:
Your commit seems not to be linked to your GitHub account. See: [Why are my commits linked to the wrong user?](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/troubleshooting-commits/why-are-my-commits-linked-to-the-wrong-user) for more info. (It's also a seemingly unrelated account with a different name, why is that?). Ah u mean email settings? Yes i use for commiting another email address then my github account. Is this required? I have one for credentials and one for contacting.


What u mean by that?

 
Did you use any AI tools to write the PR description, or write any part of the PR code? If so that needs to [be disclosed](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions) and we do not accept PR descriptions written in this way.

Code is from me, description extended by AI for better readability.

"Did you use any AI tools to write the PR description, or write any part of the PR code? If so that needs to [be disclosed](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions) and we do not accept PR descriptions written in this way" in which way u want a description? Less readable/Less explanation?

--- Zireael07:
> Code is from me, description extended by AI for better readability.

*facepalm* AI written descriptions ARE NOT "better readable", but the opposite - overly wordy

--- AThousandShips:
> What u mean by that?

Are you Stefan Kraehenmann or Justin Bobr?

> in which way u want a description? Less readable/Less explanation?

We want it clear and written by a person, not a machine, and not full of irrelevant details like what files were changed which is obvious 

Also you are mixing my comments and your own response making it impossible to read, and you copied my response twice

--- justin-bobr:
> Are you Stefan Kraehenmann or Justin Bobr?

Is ur real name AThousandShips? ;) For sure my name is not a famous polish meme.

Anyway. Which kind of "description" u want? This explains exactly the workaround and the problems i face with https://github.com/justin-bobr/eta-multiplayer. Tooks me a lot of time to find out this wonderful glitch, and its well documented by me and my friend the AI.

Greetings Stefan AKA Justin Bobr


--- AThousandShips:
Then you've answered the question I asked that was not obvious (I don't speak polish, so I obviously don't get the meme, and that's why I asked a pretty straight forward question), and please see the link to fix that it's not linked with your account. The reason I asked was mainly to help you, but also because the discrepancy between the names (as you have what looks to people who don't get the meme like a "real" name, unlike my nickname which is obviously not a "real" name, but then I don't have any other name on my commits so there's no confusion unlike this situation) 

I'm sorry but if you don't understand what is the problem with this description I don't know how to explain it better to you than I already have, but I'll try again: it's extremely verbose and unhelpfully overly detailed, and lists obvious information like what files have been changed and also lists things like the API which also is obvious from just reading the code

The description should be clear and easily navigable and no longer than it needs to be

Feature pull requests should be associated to a feature proposal to justify the need for implementing the feature in Godot core. Please open a proposal on the [Godot proposals](https://github.com/godotengine/godot-proposals) repository (and link to the proposal in this pull request's body). That's the place to add the details about *why* this is needed

Also in the future please follow the instructions in the PR template and disclose AI use and follow the format, thank you 

--- clayjohn:
Hi, thank you for your interest in contributing to Godot. However we are not accepting AI-generated PRs right now. 

Good luck with your project!


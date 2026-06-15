# PR 119058 [CLOSED] — Fix GDScript hot reload member defaults
AUTHOR: dsarno

## BODY
Fixes #119057.

Fix GDScript hot-reload migration for newly added member defaults.

Before this PR, `GDScriptInstance::reload_members()` remapped existing member values into the new member layout, but newly added members were left as default-constructed `Variant::NIL`. This could leave a migrated live instance exposing a new property while `instance.get()` returned Nil.

Example shape:

```gdscript
# v1
extends RefCounted
```

Hot-reload to:

```gdscript
extends RefCounted

var injected_dict: Dictionary = {}
var injected_array: Array = []

func describe() -> String:
    return "dict=%d array=%d" % [injected_dict.keys().size(), injected_array.size()]
```

Existing live instances should have empty `Dictionary` / `Array` values after reload. Before the fix, `injected_dict` could be Nil and `.keys()` could crash.

This PR initializes newly introduced members during hot-reload live-instance migration from compiled member defaults when available, and otherwise falls back to typed built-in defaults. Compiled defaults are assigned directly, matching normal construction semantics for constant references.

Fresh instances already worked because normal construction runs `@implicit_new()`. This fix is limited to live-instance member migration during hot reload; it does not rerun arbitrary initializer expressions or `@onready` initialization, because doing so would rerun user code and could clobber migrated values. Initializer contents that only exist in `@implicit_new()` bytecode are therefore out of scope for this narrow migration fix.

Regression coverage adds a GDScript test for:

- v1 script with no field
- live instances created from v1
- hot reload to v2 with `Dictionary = {}` and `Array = []`
- migrated instances exposing non-Nil empty containers
- calling `injected_dict.keys()` without crashing
- migrated instances not sharing their newly constructed empty containers

Related to #97834 and #98221, but this fixes a separate newly added member default migration case.

Tested locally:

```bash
scons platform=macos target=editor dev_build=yes tests=yes vulkan=no angle=no accesskit=no -j8
bin/godot.macos.editor.dev.arm64 --headless --test --test-case="[Modules][GDScript] Hot reload initializes newly added member defaults"
bin/godot.macos.editor.dev.arm64 --headless --test --test-case="*[GDScript]*"
bin/godot.macos.editor.dev.arm64 --headless --test --test-suite="[Modules][GDScript]"
git diff --check
```

**AI Disclosure**: this PR was implemented with assistance from AI-powered tools. I, a human, was in the loop to guide the tools, review their process, craft explanations and ensure overall quality as best I could. I view them and try to use them as a way to make myself a more productive and valuable contributor. And I'm always open to feedback. 🙂

## COMMENTS
--- AThousandShips:
Closing as this PR violates our contribution guidelines on AI generated code


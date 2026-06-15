# PR 120229 [CLOSED] — Mono: Fix ScriptTypeBiMap crash when C# inherits GDExtension types
AUTHOR: MLAcookie

## BODY
## Summary

Fix a `System.ArgumentException` ("An item with the same key has already been added") in `ScriptTypeBiMap` that occurs during editor hot-reload when a C# script inherits from a **non-native, non-script** base type — specifically a GDExtension-generated class.

## Root Cause

`ScriptTypeBiMap` (types.cs) maintains two bidirectional dictionaries (`_scriptTypeMap` and `_typeScriptMap`), where each `Type` may only appear once when populated by `ScriptTypeBiMap.Add()`.

`ScriptPathAttributeGenerator` (ScriptPathAttributeGenerator.cs:47-53) only assigns `[ScriptPath]` to **partial** classes whose name matches the source file and inherits from `GodotObject`. GDExtension-generated wrapper classes are intentionally non-partial, so they never receive a script path.

However, in `UpdateScriptClassInfo` (line 929), when walking a C# script's inheritance chain, the code unconditionally calls `GetOrLoadOrCreateScriptForType` for **every** non-native base type:

```csharp
// ScriptManagerBridge.cs — before the fix (lines 929-930)
var baseType = scriptType.BaseType;
if (baseType != null && baseType != native)
{
    GetOrLoadOrCreateScriptForType(baseType, outBaseScript);
}
```

`GetOrLoadOrCreateScriptForType` (line 504) treats "no script path" as "create one" — calling `CreateScriptBridgeForType` at line 534 and registering the type into `ScriptTypeBiMap`. This pollutes the bimap with entries for GDExtension types that have no script resource backing them, causing duplicate-key collisions on the next hot-reload cycle.

## Fix

Add a `TryGetScriptPath` gate before the `GetOrLoadOrCreateScriptForType` call. Only process base types that actually have an associated Godot script resource — GDExtension classes will be skipped since they lack `[ScriptPath]`:

```diff
// ScriptManagerBridge.cs:929-932
 var baseType = scriptType.BaseType;
-if (baseType != null && baseType != native)
+if (baseType != null && baseType != native
+    && _pathTypeBiMap.TryGetScriptPath(baseType, out _))
 {
     GetOrLoadOrCreateScriptForType(baseType, outBaseScript);
 }
```

This is the same guard used at line 522 to decide whether a type has a known script path. Adding it here prevents the "OrCreate" fallback for types that were never intended to have scripts.

Native Godot types are already excluded by the `baseType != native` check at line 930, so this change only affects types that are:
- Non-native (not in `Godot.Bindings` assembly)
- Non-script (no `[ScriptPath]` attribute or `_pathTypeBiMap` entry)

## Impact

- **Before**: Editor hot-reload crashes whenever a C# script inherits from a GDExtension type.
- **After**: Hot-reload works correctly; GDExtension base types are properly skipped since they have no `ScriptPath` registration.

The fix is **1 line**, idempotent, and does not affect native Godot type hierarchies.

Thank you for your time reviewing this.

## COMMENTS
--- AThousandShips:
Are you using an LLM to write the PR description? It is extremely verbose for a two line change, regardless if you wrote it yourself please remove unnecessary details and make it properly readable

--- MLAcookie:
Yes, my English isn't good enough to write long paragraphs. This is my first time sending a PR to a large project. I'll edit it a bit more.

--- AThousandShips:
You don't have to write long, in fact you absolutely shouldn't

Just describe what you changed and why, and link to any issues if there are any, if it is a major complex problem to describe please open an issue first if there is none (and *don't* use an LLM to write the issue)

Edit: this seems far too verbose still, it's a single line of code, and you don't need to repeat the actual fix in the PR description it's visible in the changed files

--- MLAcookie:
I find something new in this problem, It may be more than that problem, so I turn this to draft. Plan to post PR after stable replication and creation of related issues

--- MLAcookie:
It seems that this issue involves more than I initially thought. I will try to discuss with the team members working on the .NET integration whether it's feasible, so for now, I will close this PR. I apologize for any breach of protocol. Thank you for your time.


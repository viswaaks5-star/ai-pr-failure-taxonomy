# PR 115130 [CLOSED] — Fix crash in LineEdit when theme font is missing
AUTHOR: LanzaSchneider

## BODY
## Issue description
Godot crashes when opening a scene that contains a LineEdit control with a missing/deleted font resource from its theme.

### Steps to reproduce
1. Create a scene with a LineEdit control
2. Assign a custom font resource to the LineEdit's theme
3. Save the scene
4. Delete the font resource file from the filesystem
5. Restart the editor and attempt to open the scene again
6. **Result**: Editor crashes

### Crash details
The crash occurs in `LineEdit::get_minimum_size()` when dereferencing a null font pointer:

```
[0] LineEdit::get_minimum_size (scene/gui/line_edit.cpp:2451)
...
[23] EditorNode::set_edited_scene_root (editor/editor_node.cpp:4464)
[24] EditorNode::set_edited_scene (editor/editor_node.cpp:4443)
[25] EditorNode::load_scene (editor/editor_node.cpp:4803)
```

## Root cause
In `LineEdit::get_minimum_size()`, the code directly accesses the font from theme cache without null validation:

```cpp
float em_space_size = font->get_char_size('W', font_size).x; // Crash if font is null
```

When a font resource is missing, `theme_cache.font` is null, causing a null pointer dereference.

## Solution
Add a defensive null check at the beginning of the function. If the font is missing, return a safe default minimum size:

```cpp
if (font.is_null()) {
    return Size2(); // Return zero size if font is missing
}
```

This follows the same defensive pattern used in other UI controls and prevents the crash while allowing the editor to gracefully handle missing resources.

## Testing
- Reproduced the original crash by deleting a dependent font resource
- Applied the fix and verified the editor no longer crashes when opening the scene

## COMMENTS
--- AThousandShips:
This level of description detail is not really needed for this simple (and more importantly uncontroversial) a fix, it also reads a lot like it was written by an LLM, and even like the report or suggestion by an LLM for solving this problem, if this was written by an LLM [you have to disclose this](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions)

Please keep PR descriptions short and only containing relevant information

Also is there any issue report for this? You mention:
> Reproduced the original crash by deleting a dependent font resource

What is that original crash from? A post somewhere?

--- KoBeWi:
> the code directly accesses the font from theme cache without null validation:

That's true for most theme resources. They have a fallback in the default theme, so it's normally not possible for them to be null. I can't' reproduce the crash using the provided steps.

--- LanzaSchneider:
@KoBeWi Here's a reproduce record:

https://github.com/user-attachments/assets/4e5253ee-c1f1-437c-9f27-58d6d5a73e4d

```
[0] LineEdit::get_minimum_size (L:\harken\harken-halli-galli\engine\godot\scene\gui\line_edit.cpp:2451)
[1] Control::_update_minimum_size_cache (L:\harken\harken-halli-galli\engine\godot\scene\gui\control.cpp:1737)
[2] Control::get_combined_minimum_size (L:\harken\harken-halli-galli\engine\godot\scene\gui\control.cpp:1747)
[3] Control::_size_changed (L:\harken\harken-halli-galli\engine\godot\scene\gui\control.cpp:1765)
[4] Control::_notification (L:\harken\harken-halli-galli\engine\godot\scene\gui\control.cpp:3962)
[5] Control::_notification_forwardv (L:\harken\harken-halli-galli\engine\godot\scene\gui\control.h:45)
[6] LineEdit::_notification_forwardv (L:\harken\harken-halli-galli\engine\godot\scene\gui\line_edit.h:37)
[7] Object::_notification_forward (L:\harken\harken-halli-galli\engine\godot\core\object\object.cpp:1013)
[8] Object::notification (L:\harken\harken-halli-galli\engine\godot\core\object\object.h:930)
[9] ThemeOwner::_owner_context_changed (L:\harken\harken-halli-galli\engine\godot\scene\theme\theme_owner.cpp:76)
```

@AThousandShips Thanks for the feedback. You're right it was too verbose—I used LLM assistance because English isn't my first language and I wanted to ensure clarity, but I overdid it, sorry; The bug discovery and code fix are entirely my own work.

--- AThousandShips:
The video is far too cropped so it's not possible to really see what is going on

Please open an issue with clear details and an MRP

--- KoBeWi:
It's fine, the bug is in theme overrides.

--- KoBeWi:
As I suspected, other controls have the same problem.
E.g. Panel
https://github.com/godotengine/godot/blob/895630e853b7f389c2a3de5cfe02ef433f7b8c23/scene/gui/panel.cpp#L43-L45
Deleting the assigned StyleBox will crash too.

I tested Godot 4.5 and this is actually a regression, as previously the editor would not crash in this case. So the fix is not correct, it's a workaround for a deeper issue that should be invesitgated.

--- KoBeWi:
I opened #115150 to track this. Could use some bisecting (at least to identify which version introduced the crash).

--- LanzaSchneider:
> I opened #115150 to track this. Could use some bisecting (at least to identify which version introduced the crash).

Understood, thanks for investigating. Should I close this PR and help with the bisect instead?

--- KoBeWi:
The PR won't be merged as it is now, but you can always rework it once the actual issue is identified.

--- Zireael07:
@LanzaSchneider LLMs do NOT 'ensure clarity', they're very wordy and on top of that can just make things up. Use Google Translate, DeepL or something like that if you're not a native English speaker

--- AThousandShips:
You can also use LLMs to *translate* your own written pr description, it might be of mixed quality, but it will be your description and more to the point (and you can verify it with someone who speaks English)

--- Zireael07:
@AThousandShips LLMs are bad at translating. Use tools that are designed to translate instead of generic tools

--- KoBeWi:
The bug was caused by a core change and is now fixed on master. Thanks for the contribution nonetheless.


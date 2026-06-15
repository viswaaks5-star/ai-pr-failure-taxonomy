# PR 116418 [MERGED] — Input: Add SDL `misc2`-`misc6` gamepad button constants
AUTHOR: oCHIKIo

## BODY
## Description

Adds the missing MISC2 gamepad button constant to Godot's input system.

## The Problem

The MISC2 button string is recognized by SDL (used by Nintendo Switch 2 Pro Controller and Horipad Steam) but was not mapped in Godot's JoyButton enum. This caused the following warning repeatedly at startup:

_**Unrecognized output string "misc2" in mapping: 030000000d0f0000ab01000011010000,Horipad Steam,...,misc2:b2,..**_

This silently broke button support for controllers that use this button.

## The Fix

- Added `JoyButton::MISC2 = 21` to the enum in `core/input/input_enums.h`
- Added `"misc2"` string at index 21 in `_joy_buttons` array in `core/input/input.cpp`
- Added GDScript binding for `JOY_BUTTON_MISC2` in `core/core_constants.cpp`
- Added documentation entry in `doc/classes/@GlobalScope.xml`
- Updated `JoyButton::SDL_MAX` from 21 to 22

## Testing

Built from source and ran with `--verbose` flag. The warning no longer appears.

## Affected Hardware

- Nintendo Switch 2 Pro Controller
- Horipad Steam controllers

## COMMENTS
--- akien-mga:
For the record, your commit seems not to be linked to your GitHub account. See: [Why are my commits linked to the wrong user?](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/troubleshooting-commits/why-are-my-commits-linked-to-the-wrong-user) for more info.

Additionally, the PR description has telltale signs of being AI generated. We have a policy that requires that the use of AI assistants should be disclosed: https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions

Please clarify what you use AI assistants for (writing code, documentation, PR description, etc.) and whether you actually tested and understand the code you're submitting.

Before spending time reviewing a PR to assess whether it's addressing an actual problem and fixing it properly, we need to confirm that we're dealing with a human that did their due diligence.

--- oCHIKIo:
I only used ai assistance to draft the PR description, the debugging and implementation were done independently. I should have disclosed that upfront and will do so in future contributions , I identified the issue by running Godot with --verbose and seeing the “Unrecognized output string misc2” warning. The problem was that misc2 was missing from the enum used to index _joy_buttons, causing controller mappings to fail. I added MISC2–6 to match SDL3’s definitions, rebuilt from source, and confirmed the warning no longer appears, please let me know if any further details are needed.

--- akien-mga:
That makes sense, thanks. From a cursory check it seems correct, though we should test to be sure as these arrays can be finicky.

It makes sense to me to add all `misc*` entries supported by SDL, I see they add `misc2` to `misc6` in 2024:
- https://github.com/libsdl-org/SDL/commit/cb70e972e3
- https://github.com/libsdl-org/SDL/commit/d04fea8b87

--- oCHIKIo:
It looks like the failing check is caused by a segfault in the EXR importer during asset reimport, which doesn’t seem related to the input system changes in this PR. Is this something that’s already known as a flaky CI issue? 

--- Nintorch:
I think in the future we might want to disable Godot's internal mapping system on platforms that use SDL, because we already have one inside SDL, but that's a topic for a separate PR.

--- Repiteo:
Thanks! Congratulations on your first merged contribution! 🎉 

--- oCHIKIo:
thanks :)


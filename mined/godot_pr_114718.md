# PR 114718 [CLOSED] — Input: Add native Virtual Device Input System for on-screen controls
AUTHOR: brunosrz

## BODY
# Input: Add native Virtual Device Input System for on-screen controls

## Overview

This PR introduces a native **Virtual Device Input System** to Godot Engine. It provides a robust, high-performance architecture for on-screen controls (joysticks, buttons, touchpads) by treating them as first-class input devices. This implementation directly addresses the long-standing community need for standardized mobile input, as outlined in **Godot Proposals [#13943](https://github.com/godotengine/godot-proposals/issues/13943)** and **[#11192](https://github.com/godotengine/godot-proposals/issues/11192)**.

## Intentions & Philosophy

The core intention of this system is to provide a **"Hardware Abstraction Layer for UI"**.

Currently, developers must choose between limited `TouchScreenButton` nodes or complex, fragmented GDScript-based joysticks. This PR changes that by:

1. **Unifying Input Logic**: Game code should not care if an `InputEvent` comes from a physical Sony DualSense or a `VirtualJoystick` on an iPad. By emitting native `InputEventVirtual*` events, this system allows the `InputMap` to handle on-screen controls exactly like hardware.
2. **Performance (C++ Core)**: By moving touch tracking, vector calculations, and event dispatching to the engine core, we achieve the lowest possible latency and eliminate the frame-budget cost of running complex input logic in GDScript.
3. **Developer Experience (DX)**: Providing a suite of `Control`-based nodes that respect the layout system, the Inspector, and the Theme system allows artists and designers to iterate on mobile controls without writing boilerplate code.

## Technical Breakdown

### 1. Core Input Expansion

The `InputEvent` hierarchy has been expanded with two primary types:

- **`InputEventVirtualButton`**: Represents digital states (On/Off) from virtual devices. Supports `device_id` to allow multiple virtual controllers.
- **`InputEventVirtualMotion`**: Carries analog data (X/Y axes) for joysticks, sliders, or touchpads.
- Integration into `Input.parse_input_event()` ensures that `is_action_pressed()` and `get_vector()` work seamlessly with both physical and virtual inputs.

### 2. Architecture: `VirtualDevice` base class

A new abstract base class `VirtualDevice` (inheriting from `Control`) serves as the bridge between UI interactions and the Input pipeline. It manages:

- **Touch ID Tracking**: Automatically handles multi-touch state and focus capture across different UI layers.
- **Event Dispatching**: Logic to translate raw `InputEventScreenTouch/Drag` into high-level virtual events.

### 3. New UI Nodes (`scene/gui/`)

The system includes specialized nodes based on the requirements of modern games:

- **`VirtualButton`**: A touch-optimized button supporting various press behaviors and full theme integration.
- **`VirtualJoystick` & `VirtualJoystickDynamic`**: High-performance analog sticks with support for Fixed and Dynamic modes. `VirtualJoystickDynamic` introduces a capture area that spawns the joystick at the touch point, with a **"Visible By Default"** option to keep the joystick at a pre-defined position when idle.
- **`VirtualDPad`**: Standard 4-way directional pad for retro and UI navigation.
- **`VirtualTouchPad`**: A relative-motion area specifically designed for 3D camera controls and look-around logic.

### 4. Integration with ThemeDB

To ensure visual consistency, the system is fully integrated with Godot's **Theme System**:

- New nodes use `BIND_THEME_ITEM` to expose StyleBoxes, Colors, and Fonts.
- Default aesthetics have been added to `default_theme.cpp`, ensuring an "out-of-the-box" professional look while remaining fully customizable via "Theme Overrides".

## Why in Core?

While many third-party addons exist, they lack the deep integration required for a "first-class" experience. By bringing this to core:

- We standardize mobile development across the engine.
- We enable the official demo projects to work flawlessly on touch devices.
- We provide a performance-optimized path that is difficult to achieve in GDScript alone.

## Documentation

- Full XML reference updated for all new classes and events in `doc/classes/`.
- Updated descriptions for `Input` and `InputMap` to include virtual device routing logic.


## COMMENTS
--- brunosrz:
Did I miss something? Did I fail to implement a suggestion?

--- brunosrz:
I'm resolving the pre-commit error.

--- AThousandShips:
> Did I miss something? Did I fail to implement a suggestion?

There are several, I've marked them as unresolved, please resolve them or answer the questions in them before marking them as resolved

--- clayjohn:
I am seeing too many hallmarks of an AI agent-generated PR here. There are too many changes that make no sense and are not necessary for implementing the proposed feature, the description is obviously AI-generated, and the logs left by the AI-agent are left in the PR in the original commit. 

Please note we do not allow PRs that are made entirely by AI. It is a requirement that _you understand the code that you submit_ (https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#contribute-only-what-you-understand). Dumping a bunch of code from your AI agent on us and getting us to review the slop it produces is not acceptable. If you choose to use an AI agent to develop, you _must_ take full responsibility and review every line of code that it produces and only submit code that is useful and beneficial for the project. 

I am going to close this PR as a result. It is not fair to ATS to ask her to spend time reviewing code that you haven't even taken the time to review yourself. If you want to go ahead with this feature, then please open a new PR that:
1. You fully understand and have reviewed (or better yet actually written the code for)
2. You have tested and actually works (see the failing checks)
3. Does not include any unrelated changes suggested by the AI that are not needed for the feature

--- brunosrz:
The documentation and pull request description were indeed created by AI, as were the SVGs, but all the code was written by me. I'm a beginner in C++, this is my first real project, and I've been working on it for 2 months. I started by implementing it as a plugin and then migrated it to the engine; the code wasn't written using AI.

--- brunosrz:
I don't speak English, so I use a translator. I've also never participated in/developed anything in a group, so I don't know how to submit a pull request; that's why I used AI.

--- clayjohn:
> The documentation and pull request description were indeed created by AI, as were the SVGs, but all the code was written by me. I'm a beginner in C++, this is my first real project, and I've been working on it for 2 months. I started by implementing it as a plugin and then migrated it to the engine; the code wasn't written using AI.

I'm sorry, I don't believe you. It is extra suspicious that you are only disclosing your use of AI to generate an SVG after you have been caught. 

Ultimately, it isn't a very good idea for a beginner programmer who doesn't even know how to open a pull request to try to write 3000 lines of C++ code that they don't understand and submit it to a codebase that is running on millions of devices. We have to maintain a very high standard of quality for our code. 

That being said, you are still welcome to contribute including making another attempt that this feature. I will repeat what I said above:

> If you want to go ahead with this feature, then please open a new PR that:
> 
> 1. You fully understand and have reviewed (or better yet actually written the code for)
> 2. You have tested and actually works (see the failing checks)
> 3. Does not include any unrelated changes suggested by the AI that are not needed for the feature

If you are really interested in working on Godot and learning C++ at the same time, I recommend picking a much smaller task that will be more suitable for your skill level. 

--- Calinou:
Note that there's already an open pull request implementing a virtual joystick node:

- https://github.com/godotengine/godot/pull/110933

--- Alex2782:
> as outlined in Godot Proposals https://github.com/godotengine/godot-proposals/issues/13943 and https://github.com/godotengine/godot-proposals/issues/11192.

Proposal [13943](https://github.com/godotengine/godot-proposals/issues/13943) 

The proposal was submitted by you and was closed 4 days ago; the reasons are listed here.
https://github.com/godotengine/godot-proposals/issues/13943#issuecomment-3708522888
_The use of AI is already being criticized there as well._

---------

>  I'm a beginner in C++, this is my first real project, and I've been working on it for 2 months

https://contributing.godotengine.org/en/latest/pull_requests/pr_workflow.html

Especially for beginners, it's important to understand what the AI ​​is doing. Let your AI explain it to you, and check every answer to make sure it's correct. Free AI models often have an error rate of at least 15%.

Note: it's very unusual for a beginner to write, understand, test, and fix over 3000 lines of code within two months. Even experienced programmers with over 20 years of experience can't manage that in their free time without AI assistance. 😃 




--- brunosrz:
> Observe que já existe uma solicitação de pull request aberta implementando um nó de joystick virtual:
> 
> * [Adicionar VirtualJoystick  #110933](https://github.com/godotengine/godot/pull/110933)

And is my system just a virtual joystick node? No, it's not. I added button, dpad, joystick, joystickdynamic, and touchpad—not just nodes, but inputs as well. It's worth mentioning that there's another pull request on the same topic, if it is the same topic, but that's not the case. And about you saying I didn't test it, I did test it extensively. And I didn't mention before that I used architectural intelligence because I didn't think it was relevant/I didn't think it would harm me over something trivial.

--- brunosrz:
I tested what I did by compiling the engine and testing it in practice in games. I sent the executable to friends who also tested it. It didn't pass your criteria or the GitHub Actions criteria, but to say that I didn't test it is the same as throwing away two months of my work. You're saying it's unfair for me to submit the commit for you to review and test, but what about me, who's being penalized when I'm just trying to contribute to your work?

--- brunosrz:
In my proposal, you complained about the use of AI to produce the text, but how does text and icons made with AI impact the code that I wrote?

--- brunosrz:
Do you know where I used AI? I used it to understand how the engine's organization works, how the themedb works, I used it to create the XML documentation, the icons, and the markdowns that I presented.

--- brunosrz:
> Observe que já existe uma solicitação de pull request aberta implementando um nó de joystick virtual:
> 
> * [Adicionar VirtualJoystick  #110933](https://github.com/godotengine/godot/pull/110933)

His system uses system/user-named input events similar to a touchpad button, mine doesn't; mine is an input device, hence the name "Virtual Devices." It's not just a joystick; it consists of 5 non-abstract nodes plus 1 abstract node that is the virtual device and has logic for multitouch.

--- Alex2782:
> I tested what I did by compiling the engine and testing it in practice in games. I sent the executable to friends who also tested it. It didn't pass your criteria or the GitHub Actions criteria, but to say that I didn't test it is the same as throwing away two months of my work. You're saying it's unfair for me to submit the commit for you to review and test, but what about me, who's being penalized when I'm just trying to contribute to your work?

That sounds amazing if it works in your games! 
Why didn't you attach any pictures and videos showing your hard two months of work in action? 


You need to understand that there are strict guidelines; every new line of text increases the effort required to maintain the code. **Step 1** is to read and understand this and try to follow it as best you can to reduce maintenance for everyone involved: https://contributing.godotengine.org/en/latest/pull_requests/pr_workflow.html

However, after seeing the PR description and your proposal, I’m afraid that you won’t make an effort to read it carefully or to understand it.


# PR 111027 [CLOSED] — Added Many ai features in the godot
AUTHOR: SnapTST

## BODY
…pt support

Features:
- Complete AI Agent node with Google Gemini API integration
- TypeScript execution engine for dynamic AI behaviors
- Conversation management and persistence
- Memory system for context retention
- Extensible action framework for AI interactions
- Editor integration with AI tools and panels
- Full TypeScript definitions for Godot API
- Example TypeScript AI implementations
- Hardcoded API key support as requested

Module includes:
- AIAgent: Main orchestrating node with state management
- GeminiClient: HTTP client for Gemini API (Pro, Pro Vision, Flash)
- AIConversation: Message history and role-based conversation management
- TypeScriptRunner: Compile and execute TypeScript with Godot context
- Editor Plugin: Integrated AI tools in Godot editor
- Examples: Sample TypeScript AI agents and configurations

All classes are fully documented and integrated into Godot's class system with proper signals, properties, and method bindings.

<!--
Please target the `master` branch in priority.

Relevant fixes are cherry-picked for stable branches as needed by maintainers.

To speed up the contribution process and avoid CI errors, please set up pre-commit hooks locally:
https://contributing.godotengine.org/en/latest/engine/guidelines/code_style.html
-->


## COMMENTS
--- AThousandShips:
Thanks for opening a pull request!

Feature pull requests should be associated to a feature proposal to justify the need for implementing the feature in Godot core. Please open a proposal on the [Godot proposals](https://github.com/godotengine/godot-proposals) repository (and link to this pull request in the proposal's body).

Be aware that there's not much support for AI integration, and several proposals for this has already been rejected due to lacking support 

--- fire:
I don't think there's a proposal for this so I'll type my review comments here.

1. Godot engine doesn't have a typescript engine so adding typescript support won't work with Godot Engine core.
2. Gemini is not the only large language model, so from the perspective of Godot Engine contribution it wouldn't make sense to support only Gemini. I think cline and visual studio copilot support 5-20 large language model providers. The typical implementations of this use MCP and openrouter.
3. Since godot engine doesn't have a database built-in (see my sqlite module) I am not sure where you would store memory locally. Probably a .godot folder
4. Technical github action checks are failing

There's a one sided debate on should we add ai features.. So I'll leave that debate to other people but these are my technical review comments.

--- PaulHMason:
Personally, I'll dump Godot so fast if AI stuff is integrated into the core product. [Zenva ](https://gamedevassistant.com/)have already done something similar as an addon, so there is no need to pollute Godot when an alternative approach exists for those who care.

--- akien-mga:
Hello and thanks for your contribution.

We currently have a consensus among maintainers and the Godot project leadership that we do not want to add AI / LLM features to Godot.

So we'll close this PR as there is no intention to merge it.

Since you have made it self-contained as a module, you can consider distributing it yourself as an open source module which interested users can compile in their version of Godot, or turn it into a GDExtension for ease of distribution.


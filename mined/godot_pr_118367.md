# PR 118367 [CLOSED] — GDScript: Add compiled bytecode export option
AUTHOR: cheatdeveloper73

## BODY
## Summary
This restores compiled GDScript export for the 4.x line by serializing compiled scripts to `.gdb` files during export and loading those compiled assets back through the GDScript cache/resource loader path at runtime.

This branch is scoped to the compiled export/load path only:
- export preset wiring for compiled script output
- `.gdb` serialization and deserialization for compiled GDScript
- `.gdb` loading support in the GDScript cache/resource loader flow
- bytecode dump support for exported scripts
- regression coverage for remap loading and serializer roundtrip behavior

## Why
This is not being proposed as a brand-new workflow.

Godot 3.x exposed a "compiled bytecode" export option, but in Godot 4.x that workflow was effectively gone. On March 17, 2022, issue `#59241` reported that the option still existed in 4.0, but exported projects continued to ship original `.gd` files instead of compiled script assets:
- https://github.com/godotengine/godot/issues/59241

In the discussion on that issue, `vnen` explained two important points:
- the old 3.x `.gdc` path was essentially tokenized source, not a fully compiled script representation
- the better direction for 4.x was an intermediate representation that stores scripts already tokenized, parsed, and compiled in the export

Relevant maintainer discussion:
- https://github.com/godotengine/godot/issues/59241#issuecomment-1089458703
- https://github.com/godotengine/godot/issues/59241#issuecomment-1384520401
- https://github.com/godotengine/godot/issues/59241#issuecomment-1386122358

Related proposal:
- https://github.com/godotengine/godot-proposals/issues/8605

This change is meant to restore compiled-script export for 4.x in that direction: exported projects ship runnable compiled script data instead of loadable plaintext `.gd` sources.

This is not intended as DRM or a security boundary. The goal is to restore a compiled export workflow so projects can distribute runnable scripts without also shipping directly reusable source text in the exported pack.

## Testing
- `git diff --check`
- added a regression test for `.gdb` remap loading, self references, and typed arrays
- added a regression test for direct bytecode serializer roundtrip runtime and dump preservation
- built Windows editor, `template_debug`, and `template_release` from this branch
- verified a real exported project ran correctly with bytecode export enabled on a fresh 4.6.1-based build
- mounted the exported `.pck` with the built engine and verified it contained `79` `.gdb` files and `0` `.gd` files when enumerated through Godot's own pack loader

## Upstream note
This should be framed upstream as restoration of a missing 3.x export workflow for the 4.x GDScript pipeline, not as an unrelated new feature. That said, it still changes current 4.x export behavior, so the corresponding proposal discussion is linked above.


## COMMENTS
--- Ivorforce:
While we appreciate any effort that went into this PR, you failed to read the rules for submitting PRs. Specifically, you must [**disclose the use of AI**](https://contributing.godotengine.org/en/latest/engine/introduction.html#checklist-for-new-contributors).
Your failure to do so is a violation of our trust, and doesn't inspire confidence about how diligently this PR was created. Therefore, I am going to close it.

If you wish to contribute to Godot, please read our [rules](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html) and [contribution guidelines](https://contributing.godotengine.org/en/latest/engine/guidelines/index.html).
I also recommend starting with smaller contributions at first, since those are more likely to be reviewed and merged, while you build trust with the Godot community.

Thanks again!

--- tavurth:
@Ivorforce Given that this PR is now prior art on the topic (an actual regression from 3.x to 4.x), what would need to happen to move this forward properly?

--- Ivorforce:
We'd need @cheatdeveloper73 to be transparent about how they worked on the PR. That would eliminate the violation of our PR rules.
This is still a huge PR (2000 LOC), which is quite a lot for a new contributor. If they are interested in getting it merged, i would recommend getting involved with the contributors in chat, and perhaps (like I mentioned) contributing some smaller changes first to get used to the contribution workflow and expectations.

--- tavurth:
Ok makes sense, I actually read through the entire PR and seems well structured to me.

@cheatdeveloper73 thank you for your work on this! 🙏 Hope we can get it merged eventually

--- cheatdeveloper73:
> While we appreciate any effort that went into this PR, you failed to read the rules for submitting PRs. Specifically, you must [**disclose the use of AI**](https://contributing.godotengine.org/en/latest/engine/introduction.html#checklist-for-new-contributors). Your failure to do so is a violation of our trust, and doesn't inspire confidence about how diligently this PR was created. Therefore, I am going to close it.
> 
> If you wish to contribute to Godot, please read our [rules](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html) and [contribution guidelines](https://contributing.godotengine.org/en/latest/engine/guidelines/index.html). I also recommend starting with smaller contributions at first, since those are more likely to be reviewed and merged, while you build trust with the Godot community.
> 
> Thanks again!

Well I guess if it's important to mention, yes the PR was created using AI, for the writing here and the code itself. It was tested EXTENSIVELY against my own game project (40k lines of gdscript, a complete multiplayer tactical FPS shooter). I've verified the quality of the code, I've read through the entire design, I designed the way it works (inspiration was how unity's IL2CPP gets setup). Maybe 2000 lines of code is a lot but everything here generally needs to be here. It's not weirdly bloated and the code isn't obviously messed up. It's a feature a lot of people want, and something that should've already been in the engine.

--- HolonProduction:
I'm not quite sure we are on the same page here. The feature as it was present in 3.x is already available in 4.x. It just has a more truthful name. See https://github.com/godotengine/godot/pull/87634

Seeing that this was also linked in https://github.com/godotengine/godot-proposals/issues/4220 and that the IR proopsals stays quite vague and has no consensus, this PR lacks clear goals for me. If you worked on architecture and have clear goals with this, why not share your usecase and architecture with us in a proposal first? (Please don't use an LLM for this. It's not our job to communicate with your LLM.)

--- cheatdeveloper73:
I just talked to you. I wrote that. You guys can't even tell, and it doesn't matter. All that matters is that this is a feature that has been talked about for ages, it's the actual "intermediate representation". The code works, I've tested it extensively against MY game which is complete in terms of feature set, it's proven to be highly stable. And it's only 2000 lines all of which aren't anything more complicated than "write code to disk with the ability to put the pointers required to run it in the right slots at runtime" the "feature" in 3.x was already mentioned to not be useful for anything and completely pointless. This is what the export should actually be doing, not compressed tokens, not full source code.

--- dalexeev:
Please see our AI contributions policy. Your PR was rejected based on these rules. Code reviews are time-consuming and represent a bottleneck in our processes. So, we would like to prioritize high-quality contributions over reviewing LLM output, which can generate unlimited amounts of code.

> It was tested EXTENSIVELY against my own game project

> The code works, I've tested it extensively against MY game which is complete in terms of feature set, it's proven to be highly stable.

This is not conclusive evidence. Your project may be written in a consistent style, and you may ignore certain language features or their combinations. But they exist and are used by other users. For example, a combination of static and dynamic typing, complex dependency and script loading order, etc.

> all of which aren't anything more complicated than "write code to disk with the ability to put the pointers required to run it in the right slots at runtime"

The Intermediate Representation format must account for the dependency graph and the existence of patches and mods (a compiled script must store some hashes of its dependencies). Bytecode should not be used if any of its dependencies have changed. Given the lack of source code in the exported project, this is an unrecoverable error.

Finally, other edge cases are possible that don't currently occur because scripts are parsed, analyzed, and compiled from source code or binary tokens even after the project is exported. For example, due to differences between debug and release builds. Some APIs are only available in the editor or only in debug builds. Before saving the bytecode, we must ensure that it is identical for the source and target Godot builds (debug/release, different platforms, custom builds).

Therefore, this feature requires research and consideration of a large number of factors and specific knowledge of Godot's internals. I doubt modern AI is capable of this.

> It's a feature a lot of people want, and something that should've already been in the engine.

> And it's only 2000 lines

Just because this is an important and highly requested feature (but not necessarily a high priority[^1]) doesn't mean we should rush to review and merge every PR that attempts to implement it. We must always be careful about the design and implementation of new features, especially major features that affect the language's core pipeline and the project export system.

[^1]: Importance and demand are subjective. There are many users, and each of them has many wishes for the engine, each with different priorities. What seems extremely important to you may be less important or even irrelevant to someone else. I think that bug fixes and usability improvements to the editor are collectively more important than source code obfuscation. Intermediate Representation is more of a "nice to have" feature. If it compromises GDScript's stability, it shouldn't be merged.

--- Ivorforce:
I should note that, while testing is an integral part of a good pr, it's only one part. Another PR rule is that we require contributors to fully understand the code they submit.
Our experience with ai written PRs is that the author often isn't an experienced programmer, or at least wouldn't have been able to write the PR without an AI's help. In turn, the code often turns out to be buggy and full of technical debt, because ai simply isn't very good at making architectural decisions. This is especially important for a feature that will affect most people. By merging an ai authored PR, we'd effectively merge code nobody really understands and can take responsibility for.

--- tavurth:
The technical concerns raised by @dalexeev are valid and need addressing. The dependency hashing and debug/release parity items are worth stress-testing against a real implementation. 

Would it make sense to keep this open as a reference implementation while those concerns are worked through in a proposal? @dalexeev who would be the ideal person to ask to weigh in on such an implementation?

@cheatdeveloper73  real-world 40k line project as a testbed seems like a pretty good coverage estimate, even if we can't see the codebase itself.

--- FeldrinH:
What is the exported bytecode format based on? There are choices in the design of the bytecode representation that lead to tradeoffs for the overall GDScript implementation (both now and in the future, when new features and optimizations get introduced).

Is it using the existing bytecode format that the bytecode interpreter uses? As far as I know the bytecode format that exists in the engine right now wasn't really designed to be serialized/exported, so that seems like a fairly shaky foundation to build on.

--- cheatdeveloper73:
I believe everyone questioning should either look at the code or simply test it against one of their less 'test like' projects (anyone with a project that's moderately complex). I'm sure you will all find it's sane.

--- tavurth:
@cheatdeveloper73 I think what's mostly being said here is that: "The problem space is complex" and that "We'd like to have as close to a mathematical proof that this works as possible".

Individual testing is great (especially like in your large 40k LOC project), but then they want to make sure that someone who knows about all the edge cases has reviewed this. That way they can be sure that a complex change is not gonna break everything.

It's not that your PR is being permanantly rejected, is that you probably need to go on discord, and start a conversation with people who know about these areas of the codebase, where they can ask you questions and you can answer.

Also, @HolonProduction "_it's not our job to communicate with your LLM_" is pretty rude, regardless of Godot policy

--- stonecauldron:
> Also, @HolonProduction "it's not our job to communicate with your LLM" is pretty rude, regardless of Godot policy.

@tavurth I don't think it's rude, it's just addressing the reality that a lot of open source projects are being flooded with LLM content right now. With authors often using LLMs not only for the code but for communication as well.

This is a total disregard of maintainers' time and should not be tolerated.

(To be clear, I'd be interested in a built-in obfuscation solution for the engine, that's how I came across this PR).


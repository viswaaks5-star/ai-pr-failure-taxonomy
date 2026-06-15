# PR 119505 [CLOSED] — Prevent re-entrant script class update mutation
AUTHOR: dsarno

## BODY
## Problem

This follows up on the closed #115460 symptom report with a minimized repro and an `EditorFileSystem`-side root-cause fix. The earlier 4.6 stable workaround addressed the reported regression, but the re-entry hazard described here is still reproducible on current `master` before this patch. This PR does not change `ProgressDialog` behavior globally.

This was found while developing and stress testing `godot-ai`, which exercises editor automation paths that repeatedly update tool scripts during editor startup. The minimal repro reduces that workload to a small `@tool` script that calls `EditorFileSystem.update_file()` during editor processing:

https://github.com/dsarno/godot-115460-gdscript-repro

`EditorFileSystem::_update_script_classes()` and `_update_script_documentation()` create `EditorProgress` tasks when more than one script is pending. In the GUI editor, `EditorProgress` can pump `Main::iteration()` through `ProgressDialog::_update_ui()`.

That nested editor frame can run `@tool` script code and recursively enter pending script update processing while the outer pass is still active. For script class updates, this lets an inner `_update_script_classes()` mutate or clear `update_script_paths` while an outer `_update_script_classes()` range loop is still iterating it.

The crash can surface later while registering/removing global classes, but the corrupting invariant is the re-entrant mutation of the live pending container. The same re-entry path can also duplicate the documentation progress task.

## Fix

- Move-drain `update_script_paths` into a local `HashMap` before creating `EditorProgress` or iterating script class updates.
- Move-drain `update_script_paths_documentation` into a local `HashSet` before creating its progress task.
- Add an `_process_update_pending()` re-entry guard with a pending-rerun bit, so updates queued by nested editor frames are preserved for a later pass instead of being processed recursively.
- Route the pre-reimport script class update path through the same guard while preserving the existing class-before-documentation ordering.

If a tool script continuously queues new script class updates during every pumped editor frame, documentation updates can still be delayed until that update stream settles. This PR keeps the fix scoped to pending script update processing instead of changing progress dialog behavior globally.

## Testing

Built locally:

```sh
scons platform=macos target=editor dev_build=yes arch=arm64 vulkan=no tests=yes -j8
```

Focused doctest suites:

```sh
bin/godot.macos.editor.dev.arm64 --headless --test --test-suite='*[GDScript]*,*[Editor]*'
```

Result: 6 test cases passed, 58,688 assertions passed.

Regression repro verification with the MRP linked above:

- `GENERATED_SCRIPT_COUNT := 2`, `MAX_TICKS := 80`: finished without crash, no duplicate `update_scripts_classes`, no duplicate `update_script_paths_documentation`, no `!tasks.has` assertion.
- `GENERATED_SCRIPT_COUNT := 2`, `MAX_TICKS := 0`: smooth editor load, finished without crash, `max_re_entry=1`.
- `GENERATED_SCRIPT_COUNT := 1`, headless control: finished without crash, `max_re_entry=1`.

No automated regression test is included because the proven failure mechanism requires GUI `ProgressDialog` pumping `Main::iteration()` during editor filesystem processing. The current headless doctest harness does not directly exercise that GUI progress re-entry path without a synthetic editor integration harness.

**AI Disclosure**: this PR was  implemented with assistance from AI-powered tools. I, a human, was in the loop to guide the tools, review their process, craft explanations and ensure overall quality as best I could. I view them and try to use them as a way to make myself a more productive and valuable contributor. And I'm always open to feedback. 🙂

## COMMENTS
--- HolonProduction:
Did you use an LLM when creating this PR?

--- dsarno:
> Did you use an LLM when creating this PR?

Yes I did. Happy to answer any questions about that. The whole process, including the minimal repro -- which was the most painstaking part because it kept wanting to say "this is good enough!" when it wasn't -- took about 5 hours and much back and forth. 

I'm building an mcp for godot, and every time I find a crashing bug in the engine, I'm trying to root cause it as best I can and submit a fix. This is my third. 


--- HolonProduction:
In that case please be aware that you are required to disclose LLM assistance as per our [Contribution guidelines](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions). Please also take a look at our [Checklist for new contributors](https://contributing.godotengine.org/en/latest/engine/introduction.html#checklist-for-new-contributors).

More specifically, please write your PR descriptions by hand. LLMs are bad at writing helpful PR descriptions.

<!-- If you want to participate in the dedicated review process for LLM assisted contributions, you need to specifically request it in your response. -->

--- AThousandShips:
Please do the same for all your open PRs as well

--- dsarno:
Just to clarify -- do you think this PR is poorly written? I worked with the LLM to iterate the solution and description until I thought it was clear, minimal and easy to follow.  I don't just sic it on stuff and dump the results willy-nilly, as I know happens often and everywhere these days, including on this project. 

Happy to disclose AI help. That was why I mentioned my mcp project, but I can be more explicit going forward. 

--- AThousandShips:
No one said that, just pointed out our guidelines you need to follow, please update your PR description of this and other PRs that you've used these tools for, describing what it was used for

--- dsarno:
Will do! I was responding to the part about hand writing the PR descriptions.  Thanks. 

--- AThousandShips:
By the description it sounds like the code was entirely written by an LLM, is that correct?

--- dsarno:
Yes and no, it's a bit philosophical. It wrote the actual lines of code, yes. But that was the result of a half day process that included me discovering the crash, pushing the LLMs to investigate different hypotheses about it, then iterating many times to get the minimal repro (again, it kept wanting to submit a bigger repro that was not minimal enough for me to understand the root cause). Then when the root was clear I made (had it make if you prefer)  multiple builds testing increasingly minimal solutions, both live tests and via the harnesses. I then ran multiple rounds of code reviews by different LLMs, and worked with them to craft the issue and PR until they read well and clearly to me.

So the short answer is yes it wrote the code. The longer (imho more meaningful) answer is that I drove the process, problem solving and QA. And I understand the code, the bug and the solution. 

Is that a workable approach? I'm trying to be a useful and friendly contributor. Not here to ruffle feathers!

--- AThousandShips:
That is not permitted as per our guidelines, philosophy or not, please be open and honest about this in the future, and if you want to contribute in the future please write the code yourself and respect the contribution guidelines

--- dsarno:
I'm sorry you feel that way. I had just added the disclosure as you asked. My first PR, which you reviewed, started with the disclosure, and this one prominently mentioned my ai project, so I haven't been trying to hide anything. It's just the way I work. 

That really stung to be mass banned like that, after spending so much time working to isolate difficult bugs and improve the project.  That was probably 30 hours of (my, human) work you erased, which was all done purely to be helpful. Ouch. 

I at least wish you would've closed them because they were low quality. 

--- AThousandShips:
You have not been mass banned the PRs were closed because they violate our guidelines, please read them thurougly, also that first PR did not disclose AI use at all and it doesn't say the code was generated, and the one I reviewed was a different one from the one you mentioned AI in

If you are interested in contributing you are welcome to do so if you follow the guidelines

--- dsarno:
>  that first PR did not disclose AI use at all and it doesn't say the code was generated

Very top of first PR:
>> Note to maintainers: This is not an AI slop PR.. I'm the lead maintainer on the 8,000 star Unity-MCP project. I do use LLMs to build (like many engineers), but I also make sure changes are minimal, follow project culture, and are well tested. I rebuilt Godot with the fix and tested it thoroughly. Just thought I'd let you know. 

The guidelines say "please be transparent about how you created your contribution", not that use of AI to write code is prohibited.  

I immediately added the disclaimer when you asked this time, and would have for all contributions in the future. But it'd be nice to have a little more beginner's slack, given the amount of time and care I put into them. They're real bugs, and represent real human work and knowledge. It seems a shame to just throw them away. 

Anyway, it's late here. Have a good night. 

--- AThousandShips:
It says:
> and contributions made entirely by AI are prohibited.

You are talking about the checklist, you need to read both

I'm sorry you feel that you have wasted time, but we have our guidelines, you were given plenty of slack by this conversation to clarify your use and we helped you to follow the guidelines even though you failed to do so at first, instead of outright rejecting the PR because it violated them

Have a good night


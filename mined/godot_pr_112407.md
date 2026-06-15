# PR 112407 [CLOSED] — Added More Docs
AUTHOR: hayden3456

## BODY
This PR adds source-linked, auto-generated docs for the codebase. Before you dismiss it: it includes inline source references, architecture diagrams, and I think it does a solid job. No hard feelings if you’d prefer not to include it.

If you find it useful, I’m building a documentation copilot to help explain why code is the way it is. It will:
- Auto-sync docs 
- Asks a few questions on PR's to gather understanding as to why
- Visualize the system at different levels of abstraction

I'm just building this out and would love to chat about what would help most so I can build something genuinely useful.
docforge.net

## COMMENTS
--- AThousandShips:
Thank you for your contribution, however this is not a format we use for documentation, nor is it something anyone has really asked for or something that's needed.

Generally (we are in the process of codifying our policy on generated content) we do not accept purely LLM generated content for various reasons (including practical and legal ones)

Just from a glance (I haven't done anything beyond a basic glance) I can find several obvious errors just in the code and markdown, like invalid links linking to nowhere (`[Engine Initialization and Core Systems](#1.1)`, `[Platform Abstraction Layer](https://github.com/godotengine/godot/blob/4219ce91/1.3)`, etc.) or ones that are incorrectly formatted (`[platform/windows/detect.py:47-59]()`), it also seems to grab blocks of code at random with no logical grouping for the links. I assume this is because of unfamiliarity with the syntax and not because the content wasn't checked before posting and that the text itself is correct and that you have checked that it hasn't made any other mistakes?

--- Ivorforce:
I'm closing this as we have no intention of merging it.

Thank you for the effort, though. If you think it could be useful for people using the engine code, perhaps you'd like to upload it under your own account? Just make sure you clearly identify it as AI generated content.

--- hayden3456:
@AThousandShips + @Ivorforce You are absolutely right that the docs weren't good enough. AI just isn't there yet to understand all the intricacies of a whole codebase. I'm sorry for taking up your time. Given that feedback, I'm thinking of making a CI tool that helps small incremental documentation changes solely off what the dev says, as little AI as possible. If either of you would be willing to give a few thoughts, that would be great, but no worries. Thank you again. 

--- AThousandShips:
No worries! We don't have an officially stated position on this yet but we are working on one so it wasn't easy to know


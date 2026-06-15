# PR 117326 [CLOSED] — Editor: Add "Reveal in Tree" shortcut to clear filter and show selected node/file in hierarchy
AUTHOR: MRxRadex

## BODY
Adds a "Reveal in Tree" action (default shortcut: `F`) to the Scene Tree and FileSystem docks. When a filter/search is active, it clears the filter, expands parent nodes, and scrolls to the selected item — revealing its position in the full hierarchy.

The shortcut only fires when the filter is active. Otherwise `F` passes through to the Tree's built-in incremental search. Typing `F` in the filter text field still types the letter normally. No conflicts with viewport shortcuts.

A context menu entry is also added, visible only when the filter is active.

### Demo

**FileSystem** — new "Reveal in Tree (F)" option:
<img width="508" height="396" alt="image" src="https://github.com/user-attachments/assets/690d55ae-9f30-49d3-9b9c-60e626055abd" />

**Scene Tree** — new "Reveal in Tree (F)" option:
<img width="527" height="569" alt="image" src="https://github.com/user-attachments/assets/c85ecce0-91fd-42a5-a64c-d8d16b77118c" />

**Video of the feature**:

https://github.com/user-attachments/assets/afc9ba38-1e2d-4e51-adfe-6252e64559b5

### AI Disclosure

Code was written by an LLM (Claude) based on my directions, then reviewed, tested, and iterated on by me.

## COMMENTS
--- AThousandShips:
> All changes were proofread and verified to follow Godot's coding conventions and existing patterns.

To be clear: You wrote the code with suggestions from an LLM, you didn't ask it to write the code and then proofread it?

Also did you use it to write the PR description? It's unnecessarily verbose, please trim it down to relevant information


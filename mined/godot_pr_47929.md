# PR 47929 [CLOSED] — Allow using Ctrl + Y to redo actions in the editor
AUTHOR: Calinou

## BODY
This is already possible in TextEdit nodes (including the script editor), but this change allows using <kbd>Ctrl + Y</kbd> in the 2D and 3D editors as well.

The existing <kbd>Ctrl + Shift + Z</kbd> shortcut is still available. Both shortcuts will remain supported to avoid breaking user expectations.

I've done some quick testing and script editor redo still works as expected. Feel free to test this further locally :slightly_smiling_face:

Before cherry-picking this to the `3.x` branch, remember that it uses a different shortcut handling system. I'd make sure to test this thoroughly on the `3.x` branch before cherry-picking.

## COMMENTS
--- deralmas:
I don't know, wouldn't it be redundant to have both? I mean, I have never seen a program having both. IMO we should choose either one or the other and then make whatever uses the old shortcut use the new one.

--- Calinou:
> I don't know, wouldn't it be redundant to have both?

Technically, it's redundant, but here, I think the principle of least astonishment matters more. In 2021, applications still haven't settled on using a single redo shortcut. When an application supports only <kbd>Ctrl + Y</kbd> or <kbd>Ctrl + Shift + Z</kbd>, it'll break user expectations sooner or later.

--- deralmas:
> Technically, it's redundant, but here, I think the principle of least astonishment matters more.

Ehhh... Honestly, for such a split shortcut astonishment wouldn't be that bad either, after all other applications have this issue too. I feel like anybody making games is kind of used to this. Look at blender, krita and vscode for example: they use ctrl + shift + z while other programs such as gimp and llms use ctrl + y. Maybe we could use the most common one by looking at what's used most in programs used in game development?

> In 2021, applications still haven't settled on using a single redo shortcut.

By that logic, I don't think choosing both is going to help with this issue.

I'm still uncertain whether this PR is the right choice to make. I'll think about it. For now though, IMO this could be avoided, as pretty much the only affected users would be people completely inexperienced with computers if we go for the (less common in windows, but IMO superior) ctrl + shift + z route, but a quick read of the manual could fix this. Also, if the rebindable editor shortcuts PR got merged (has it?) one could choose by themselves which one to use, eliminating the problem altogheter.

--- Calinou:
@Riteo Since <kbd>Ctrl + Y</kbd> isn't used for anything in the editor right now, I see no downside to supporting both shortcuts.

--- Duroxxigar:
> 
> 
> @Riteo Since Ctrl + Y isn't used for anything in the editor right now, I see no downside to supporting both shortcuts.

This is assuming people haven't set shortcuts on their own. I know I have to reset some shortcuts every time Godot decides to change a default shortcut.

--- akien-mga:
I don't understand why this PR would be needed? `ui_redo` is already defined with both <kbd>Ctrl+Shift+Z</kbd> and <kbd>Ctrl+Y</kbd>, so both should already work, like in the script editor, no?  CC @EricEzaM 

--- EricEzaM:
@akien-mga Yes, text edit and such get multiple bindings for actions because they directly use the input map. Other parts of the editor use the `Shortcut` class, which only has one binding allowed. That is why I did #48009. Maybe we could make that support any amount of shortcut bindings? That would also allow us to unify the shortcut editor instead of having two different sections.

--- deralmas:
Can this be closed? Just tested the editor and I can redo with both Ctrl + Shift + Z and Ctrl + Y. I think this PR has been long superceded by #51273.

--- akien-mga:
Superseded by #51273.


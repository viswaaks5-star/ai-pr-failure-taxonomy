# PR 116398 [CLOSED] — Add diagnostic logging to Forward+ pipeline creation failure
AUTHOR: glkdrlgkrlzflnjkgh

## BODY
This PR adds logging to the  forward+ clustered renderer when it fails to be created. the second modified file? I honestly have no idea what modified it.

*Bugsquad edit:*
- Intended to help troubleshoot #116313

## COMMENTS
--- glkdrlgkrlzflnjkgh:
This PR adds more detail to what is logged when the render pipeline creation in 3D forward+ clustered wirth vulkan fails

--- glkdrlgkrlzflnjkgh:
OH. sorry about the code formatting.

--- Calinou:
Can you describe why this additional print is needed? Are you trying to troubleshoot a crash that occurs on a player's device?

--- glkdrlgkrlzflnjkgh:
I have ran clang-format and setup the pre commit hooks. 

--- glkdrlgkrlzflnjkgh:
I have updated this PR with a new commit.

--- Zireael07:
@Calinou They are trying to diagnose #116313

--- glkdrlgkrlzflnjkgh:
good. 20/20 checks passed. now all  i need is someone to review it.

--- glkdrlgkrlzflnjkgh:
I am not sure how those changes occured. Although I could diff and take a look?
________________________________
From: Hugo Locurcio ***@***.***>
Sent: 07 March 2026 5:53 PM
To: godotengine/godot ***@***.***>
Cc: Callum ***@***.***>; Author ***@***.***>
Subject: Re: [godotengine/godot] Add diagnostic logging to Forward+ clustered renderer (PR #116398)


@Calinou requested changes on this pull request.

You should undo the changes that were done to platform/web/package-lock.json, as they are unrelated.

—
Reply to this email directly, view it on GitHub<https://github.com/godotengine/godot/pull/116398#pullrequestreview-3909222903>, or unsubscribe<https://github.com/notifications/unsubscribe-auth/A3FHBBKZYGKKSXLZUGIONHT4PROZJAVCNFSM6AAAAACVMCHJ5GVHI2DSMVQWIX3LMV43YUDVNRWFEZLROVSXG5CSMV3GSZLXHMZTSMBZGIZDEOJQGM>.
You are receiving this because you authored the thread.Message ID: ***@***.***>


--- glkdrlgkrlzflnjkgh:
The file change to the package lock was caused by my version of npm, I think it could be newer than the one that was originally used to generate the file. sorry about that. 

--- glkdrlgkrlzflnjkgh:
I have just now, reverted the changes made in the web package lock JSON file.
Hopefully everything is ready to merge! :)

--- glkdrlgkrlzflnjkgh:
Done. we are ready to merge. I think. I have done the changes. Just say when its ready :)

--- glkdrlgkrlzflnjkgh:
I git restored. then committed and rebased. then i pushed.

--- glkdrlgkrlzflnjkgh:
I need workflow approval. Since i made my changes.

--- akien-mga:
Could you squash the commits? See [PR workflow](https://contributing.godotengine.org/en/latest/pull_requests/creating_pull_requests.html#the-interactive-rebase) for instructions.

--- glkdrlgkrlzflnjkgh:
DOH! I thought i had squashed those. Obviously not.

--- glkdrlgkrlzflnjkgh:
I have squashed my commits into one. are we ready now?

--- akien-mga:
Not yet, as the resulting commit message isn't properly formatted:

<img width="603" height="446" alt="image" src="https://github.com/user-attachments/assets/7446d658-d204-41ed-8551-0ea2813fce7f" />

The title of the commit should be a clear description of what the commit does, not that it was a squash. And the rest of the body of the commit is made up of the messages of past commits which have been squashed, which we don't care about for the resulting history that would be merged.

See https://github.com/godotengine/godot/blob/master/CONTRIBUTING.md#format-your-commit-messages-with-readability-in-mind

--- glkdrlgkrlzflnjkgh:
(Okay maybe I shouldn't of squashed that with github desktop.)

--- glkdrlgkrlzflnjkgh:
One problem: i'm not sure how to edit the message to format it properly.

--- glkdrlgkrlzflnjkgh:
as I've already committed it and pushed.

--- akien-mga:
```
git commit --amend
git push --force origin forwardplus-logging
```

--- glkdrlgkrlzflnjkgh:
Just pushed the squashed commit. Updated the formatting of the message. hopefully it will be OK now?

--- akien-mga:
It isn't:
<img width="624" height="206" alt="image" src="https://github.com/user-attachments/assets/34c0f821-097a-40ae-a366-96d38615c5a2" />

You edited the commit, but wrote another "bad" commit message (see what I mentioned above). And then instead of force pushing like I wrote, you merged your original branch on top of the amended commit so now you have 3 commits.

I can help fix it up, but I've already had quite a bit of time spent in back and forth on this PR and this comment still stands and concerns me:
https://github.com/godotengine/godot/issues/116313#issuecomment-4197724350

Did you test this PR? Does it help? Was it AI generated?

--- glkdrlgkrlzflnjkgh:
Closed as I just remembered the crash isn't happening anymore.


# PR 36331 [CLOSED] — Dragging a node under the last item of the tree raises it a level
AUTHOR: giarve

## BODY
A children node couldn't be taken out of the father without scrolling back to the parent node icon
and thus making very troublesome to rearrange a children to be a sibling of its parent if the list of the nodes was long.

By adding an extra dragging line at the end of any children tree we can ensure that the user can move without effort a children up to parent's level even if the parent is many nodes away.

![dragging](https://user-images.githubusercontent.com/45542433/74770082-d5da3280-528b-11ea-970a-c71845389fe0.gif)

If needed, spacing or thickness for the new line can be increased.

EDIT: As requested, thickness has been increased from 1 to 2.

Fixes #34033.

## COMMENTS
--- marcospb19:
It is possible to make the lines at the bottom thicker, like 2 or 3 pixels? It looks very hard to aim.

And for this to be merged I also think that aiming below everything should bring the node to the top level (below the root). This PR currently does not implement it.

--- Zireael07:
+1 to making lines thicker.

--- akien-mga:
Is this still relevant? The issue was closed as fixed in 3.5.

--- KoBeWi:
The PR seems to do more than fixing the issue. Needs rebase though.

--- pafuent:
@giarve, @akien-mga and @KoBeWi 
This could be closed, it was implemented in another PR
![NodeDrag](https://github.com/user-attachments/assets/3b7026cd-ecdc-438f-bab1-e97fa4857f55)



--- giarve:
> @giarve, @akien-mga and @KoBeWi This could be closed, it was implemented in another PR ![NodeDrag](https://private-user-images.githubusercontent.com/6979945/377436598-3b7026cd-ecdc-438f-bab1-e97fa4857f55.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjkxNjQxNjgsIm5iZiI6MTcyOTE2Mzg2OCwicGF0aCI6Ii82OTc5OTQ1LzM3NzQzNjU5OC0zYjcwMjZjZC1lY2RjLTQzOGYtYmFiMS1lOTdmYTQ4NTdmNTUuZ2lmP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI0MTAxNyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNDEwMTdUMTExNzQ4WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZGQxYjU4N2FlNzk1YmExMDRiNjg4MTZiMDI3NDdmYTRhNzg1NDYwYmU4M2ZhNDZjN2U2ZmI4ZDAxOGM5NWZlNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.E7uBHpFYgSIozHPYVHV4e5Ve-gAJa4-HIZmOCQSgmhY)

@pafuent 
Can you check which PR is it? I cannot believe there are two PRs doing the same and they are not referenced at all...

--- pafuent:
@giarve before posting my comment I did a quick search of that PR but I had no luck. But as you can see on the GIF that I attached, the behavior is there (unless there is something that I didn't get it properly)
I did the test on the latest master and I just also tested on 4.3 stable and it's also implemented there.

--- giarve:
Well... maybe we will never find out 😂 . I used copilot to search through the PRs and nothing pops. It is weird because the behavior is exactly the same.

However, it's been 4 years since this PR, and it is solved somehow. 

Closing.


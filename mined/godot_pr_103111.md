# PR 103111 [MERGED] — Fix CanvasLayer 'Follow Viewport' documentation to match its behavior
AUTHOR: rt9391

## BODY
Fixes #103031 
The doc of follow_viewport_enabled in #99754 tells the opposite thing. 
This PR swaped enabled/disabled description to match actual behavior.

## COMMENTS
--- Meorge:
Nice!

I think it might make sense to flip the order of the two sentences, so that the behavior when enabled is described first. 

Additionally – and this might be out of scope for this specific PR's intention – the description of "maintains its position in world space" *could* be have a little more description/example to it. Something like "It can move off-screen if the camera moves away from it" (rough draft, of course). But, as I suggested before, this might be something for us to work on in a later PR, so that this fix of objectively incorrect documentation can get merged in ASAP first.

--- rt9391:
> I think it might make sense to flip the order of the two sentences, so that the behavior when enabled is described first. 

Make sense, i`ll be changing that part.

--- AThousandShips:
You accidentally changed the author of some unrelated commits, to fix this please use:
```
git reset --hard f64861d47c5dfbe75ff598ae6d7acdd4b423e51f
```
And then push with
```
git push --force
```


--- rt9391:
> You accidentally changed the author of some unrelated commits, to fix this please use:
> 
> ```
> git reset --hard f64861d47c5dfbe75ff598ae6d7acdd4b423e51f
> ```
> 
> And then push with
> 
> ```
> git push --force
> ```

Fixed! Thanks for the tips.

--- MadeScientist:
Thanks for fixing it. I have also been confused before.

--- unvermuthet:
I don't think this needs more testing.

The `Follow Viewport` name is kind of confusing, since it's actually following the world space. The Viewport doesn't move. Renaming it would be breaking and you did a good job of making the behaviour clear in the member description. This is a good fix.

--- Mickeon:
I think it may be a good call to deprecate this property and come up with another name. I've seen this being a pain point for way too many users for years.

--- unvermuthet:
It's truely confusing... But I think this doc change should be merged for versions prior to such a deprecation.

--- revaraver:
Yes, this kind of error made me doubt my doubts about viewport, screen, chatgpt and even deepseek. I tried to convince myself that the document was correct and I misunderstood the terminology during the game. Such a low-level error should not have happened.

--- Repiteo:
Thanks! Congratulations on your first merged contribution! 🎉 


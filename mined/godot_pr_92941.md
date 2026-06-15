# PR 92941 [MERGED] — [3.x] Fix physics tick counter
AUTHOR: lawnjelly

## BODY
The counter is now incremented at the start of a physics tick rather than the end.

Fixes #92903

## Notes
* Full details on the problem in the issue.
* This also fixes a knock-on potential regression in the `Input.is_action_just_pressed()` that occurs when the counter is changed.
* Some uint counters are initialized to -1 to ensure they register tick 0 as a change.
* It turns out there's actually very little in core that depends on the tick count, so it may be less prone to regressions than I initially thought.

## Discussion
There are some input considerations for changing the tick increment timing: the `pressed_physics_frame` of the action is used to determine whether input has _just_ been pressed (i.e. `is_action_just_pressed()`).

This was previously set to the current physics tick, which was fine providing this was not incremented until _after_ the tick. However, now the tick is incremented at the start of the tick, we have to account for two situations:

1) Agile input being flushed at the start of the tick
2) Input coming in _during_ the current physics tick

The key problem with (2), which was already present (but may not have occurred in the wild) is that multithread input coming in part way through a physics tick could have been missed if the `_physics_process()` to detect it had already run.

This PR sets the action physics tick to the **current + 1**. This ensures that input coming in within the physics tick will never be missed. As a result of this, the regular agile flushing with `flush_buffered_events()` is (as before) set to take place _before_ the physics tick begins (especially the tick increment). This ensures that input from `flush_buffered_events()` is processed as quickly as possibly, on the tick that begins straight after the flush.

### Future considerations
I am not absolutely sure that agile flushing should logically best take place _outside_ the physics tick, however that is the position that @RandomShaper added it originally, so to keep this PR as simple as possible and reduce risk of regressions I'm keeping that order for now.

<!--
Please target the `master` branch in priority.

Relevant fixes are cherry-picked for stable branches as needed by maintainers.

To speed up the contribution process and avoid CI errors, please set up pre-commit hooks locally:
https://docs.godotengine.org/en/latest/contributing/development/code_style_guidelines.html
-->


## COMMENTS
--- lawnjelly:
> I can't really spot a visual difference before and after this PR though.

Luckily it seems (so far) in engine internals little depends on the tick count being correct, so ideally there will be no change / before after. :+1: 

The input is most affected (particularly the just pressed logic), so I want to double check that when I get a spare moment, before moving out of draft.

It's good to fix though because user projects may depend on this, and the tick count is more important to be correct when using physics interpolation, to prevent bugs.

--- lawnjelly:
I've had a proper look through the input now, and it seems to make logical sense in the different scenarios.

There is some potential for regressions in the input (particularly slight timing differences), but I *think* everything should operate as before with the `+1` change.

I'm slightly in two minds about whether to merge before 3.6 or leave to 3.7, however it is a bug fix, and quite easy to revert if necessary, so maybe we should go for it. The worst likely problem is slight timing difference in rare circumstance.

Also although there is an approval any further testing would be appreciated as I have moved the tick increment to after the input flush since then. :+1:  

--- belzecue:
> I'm slightly in two minds about whether to merge before 3.6 or leave to 3.7

And there's my cue.  Enter Stage Left: ME in the role of THAT GUY.  Looking uncomfortable and clearly not wanting to be THAT GUY, I point to an overhead sign that reads:

> Waiting 4 Godot 3.6
>  445 
> DAYS

One one hand there's the unwavering, awe-inspiring, and endlessly amusing "commitment to the bit" that comes with the engine name and not shipping 3.6 for 445 days with no end in sight :)  On the other hand that's 445 days waiting for my own little physics fix to enter an official 3.x build :(

Given this fix is more of an edge case and likely to make no difference to most projects, I favor getting 3.6 out the door and leaving this one to 3.7.  BUT, I don't deny the Chaotic Neutral in me wants this endless 3.6 beta to become a thing of legend whispered around the campfire by my grandchildren's children.

p.s. You personally are amazing.  Everyone still working on 3.x is amazing.  A release this year would be amazing!


--- lawnjelly:
Haha, yeah sorry it's taking ages. Things have improved quite a bit lately but there are still review bottlenecks.

There's no right / wrong answers but I'm inclined to think we should test this in the next RC. There's actually just one PR waiting for a review (#92105) before we can make the RC (possibly a couple of small bug fixes too but not necessary).

--- lawnjelly:
Let's give this a spin. If there are any input regressions we can revert easily.

--- lawnjelly:
Thanks!

--- oeleo1:
@belzecue Your plea for Godot 3.6 sound like a poem. When it comes out, I promise I'll ask ChatGPT to white another one of these ;-)

In the digital vast, where ideas collide,
Godot stands tall, with open source pride.
A beacon of freedom in game design's night,
A tool of power, of might.

Where nodes connect in a dance of fate,
Scenes come alive, opening the gate.
To worlds unimagined, stories untold,
In Godot's hands, they boldly unfold.

No king's ransom to use its might,
For Godot's gift is free as light.
In this engine's glow, developers find,
A community strong, generous, and kind.

So let's craft a tale in pixels and hues,
With Godot's aid, there's nothing to lose.
From the simplest sprite to the grandest scene,
In the realm of Godot, we all are seen.

@lawnjelly  Happy to see we're getting close to the RC. Thanks.

--- matmas:
@rburing When I try MRP of #93339 with this PR there is now a new befavior when you click on the "Show NinePatchRect" button when the ball is visible. You can see the NinePatchRect streaking from the left. When the ball spawns no streaks are visible, only when you manually click the button. You can see it much more clearly when you set `common/physics_fps=10` and `settings/fps/force_fps=0`. Here is a video:

https://github.com/godotengine/godot/assets/499286/09a9b722-d67a-4b76-b47d-9311723af30e

The streaks were not visible before this PR.

--- lawnjelly:
@matmas moved discussion to #94060, as it was something I was aware of, and is not directly related to this PR afaik.

--- oeleo1:
This is a dev discussion area, but since there is no kudos area, I am chirping this feedback here.

The 3.6-rc1 is very good and the FTI work + bugfixing is especially appreciated. Due to the propagation of the FTI logic down the viewports (fixed in this release), it solved a number of visual glitches in our project and identified places where we had to add `reset_physics_interpolation()` calls for objects changing position drastically (like global_/position.x += delta_x). That's all. The result is a smooth output on 60 and 120 fps rendering devices (Apple) where previously we had "vision split" at 120 fps - the objects movement was delayed by 1 frame on odd frames, and was on time on even frames. So all in all - terrific work here, especially by @lawnjelly ! Thanks.

We did notice however some new streaking effects like the ones reported by @matmas but since we do not use `get_global_transform_interpolated()` I believe this streaking is due to some missing reset interpolation calls as explained above.   There is no MRP to report as it happens sporadically and a reset call usually solves it. Testing so far reveals a noticeable, not to say, marvellous improvement.

We have yet to test this extensively on VRR Apple Pro devices where things get trickier, but that's for another day. No bugs to report at this point, which is pretty good news.

Keep up the good work!


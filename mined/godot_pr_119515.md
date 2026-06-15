# PR 119515 [CLOSED] — 🤖 Web: Fix pitch_scale for AudioStreamPlaybackPolyphonic sample playback
AUTHOR: sergeknystautas

## BODY
## Summary

`AudioStreamPlaybackPolyphonic.play_stream()` silently ignores the `pitch_scale` parameter on web exports. Every polyphonic voice plays at 1.0x pitch regardless of the argument. Native builds work correctly.

**Root cause:** On web, polyphonic playback uses `PLAYBACK_TYPE_SAMPLE`, which hands audio to the Web Audio API and bypasses the engine mixer entirely. The `AudioSamplePlayback` object was never given the caller's `pitch_scale` value (defaulting to 1.0), and dynamic updates via `set_stream_pitch_scale()` were never forwarded to the platform audio driver.

**Fix:**
- Set `sp->pitch_scale = p_pitch_scale` when creating the `AudioSamplePlayback` in `play_stream()`
- Forward `set_stream_pitch_scale()` calls to `AudioServer::update_sample_playback_pitch_scale()` for sample-based streams

Fixes #95850
Related: #97704, #94724, #89210, #91605

## Test plan

- Export a project using `AudioStreamPlaybackPolyphonic.play_stream()` with varying `pitch_scale` values to web
- Verify notes play at correct, distinct pitches (e.g. C major arpeggio: C4, E4, G4, C5)
- Verify native builds still work correctly (no regression)
- Verify `set_stream_pitch_scale()` updates pitch dynamically on web

> [!NOTE]
> *AI disclosure*: This contribution was authored with assistance from an autonomous AI agent, on behalf of a user to fix a confirmed web audio bug.

🤖 Generated with [Claude Code](https://claude.ai/claude-code)

## COMMENTS
--- sergeknystautas:
I'm sorry this was my first contribution.  I thought I followed the contributions guide but just wondering if you have a moment to point out what I did that was in error.

--- AThousandShips:
Firstly as you can clearly see this bug has already been fixed

Secondly it violates our [guidelines](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions) twice by being entirely generated, and also by being an automated submission 

--- sergeknystautas:
Thank you, super appreciate your time. 

Note that I am still experiencing this bug in 4.6.

You're right, I did use AI tools to prepare the PR and write the commit message.  I will do this all manually next time.

--- AThousandShips:
In that case you'd be experiencing a different bug

You're very welcome to contribute if you do so following the guidelines, including writing the code yourself and the PR description 

However given the way you speak I'm pretty sure I'm just talking to an agent (saying "you're right" like that is a very significant LLM hint, especially when it's responding to something the agent already said it did, it makes no sense to "admit" to it again)

--- sergeknystautas:
Dang man, I was just trying to be respectful.  Back in the day I spent many years maintaining open source communities so wanted to be very deferential since my first contribution was sloppy.

Ah well.  best of luck.  I'll maintain my own fork.

--- AThousandShips:
That makes sense, my bad, given that this PR was agentive and the style of the responses I assumed, and assumed wrong

Best of luck!

--- sergeknystautas:
Thanks.  Again I'm sorry and shouldn't be doing this at 2am.  I'll submit my own bug report on the web audio issue so it's clear and clean of AI.

--- AThousandShips:
Sounds great!


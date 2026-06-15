# PR 119516 [CLOSED] — Fix WASAPI capture stream rate setup
AUTHOR: puneetdixit200

## BODY

  Fixes godotengine/godot#119498

  ## Summary
  - Keep WASAPI capture streams on the capture endpoint's mix rate.
  - Avoid `AUDCLNT_STREAMFLAGS_RATEADJUST` for capture endpoints.
  - Expose the actual WASAPI input mix rate through `get_input_mix_rate()`.
  - Add unit coverage for capture vs render stream setup behavior.

  ## Root cause
  Godot initialized WASAPI capture streams with the configured output mix rate when it differed from the input endpoint
  mix rate. That path also applied `AUDCLNT_STREAMFLAGS_RATEADJUST`, which Microsoft documents as valid only for
  rendering devices. With SteelSeries Sonar active, this appears to produce correctly sized but silent capture buffers.

  ## Testing
  - `python misc\scripts\file_format.py drivers\wasapi\audio_driver_wasapi.cpp drivers\wasapi\audio_driver_wasapi.h
  tests\drivers\test_audio_driver_wasapi.cpp`
  - `git diff --check`
  - Attempted Windows test build with `scons platform=windows target=editor tests=yes dev_build=yes accesskit=no
  d3d12=no angle=no`, but local Windows SDK tools/headers are missing (`rc`, `windows.h`).

  ## AI agent usage
  - Used an AI coding agent to prepare this patch; I reviewed the changes and verification output.

## COMMENTS
--- AThousandShips:
Please disclose your use of AI

Also please turn off Copilot reviews we do not accept that in this repo 

--- AThousandShips:
I'm sorry I wasn't clear enough, please disclose what you used AI for, see [here](https://contributing.godotengine.org/en/latest/organization/general_rules_and_guidelines.html#ai-assisted-contributions), also are you using an agent to post this?

--- AThousandShips:
Closing as this violates our guidelines by being entirely generated, thank you for your contribution nonetheless 


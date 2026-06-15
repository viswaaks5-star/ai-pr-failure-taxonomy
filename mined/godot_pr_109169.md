# PR 109169 [MERGED] — [Windows] Additionally use `cpuid` instruction to detect SSE4.2 support.
AUTHOR: bruvzg

## BODY
Fixes https://github.com/godotengine/godot/issues/109167

Seems like some older versions of Windows 10 might not support `PF_SSE4_2_INSTRUCTIONS_AVAILABLE` flag.

`cpuid` check should be sufficient, but I'm keeping both for possible edge cases.

Tested with `MinGW/GCC`, `MinGW/LLVM`, `MSVC`, and `MSVC/clang-cl`.

## COMMENTS
--- Repiteo:
Thanks!


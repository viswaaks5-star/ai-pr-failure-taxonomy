# PR 94109 [MERGED] — SCons: Pass optimization flags to the linker too, needed by Emscripten
AUTHOR: akien-mga

## BODY
- Fixes #94088.
- See also #91800.

Needs testing with various compilers to confirm that it doesn't have a negative impact / cause errors to pass those to the linker for MSVC, GCC, and Clang.

From a quick test with GCC, both with and without LTO, it didn't seem to make a difference in my tests.

## COMMENTS
--- Repiteo:
Doesn't look like the MSVC linker can use the optimization flags

--- akien-mga:
> Doesn't look like the MSVC linker can use the optimization flags

I tried to use ChatGPT as a "read tech docs for me and summarize it", but sounds like I wasn't critical enough of its claim that those flags impact MSVC whole-program optimization :P

--- akien-mga:
Just pointing out the regression in #94725 for myself, so I don't cherry-pick this change before we've solved that too.


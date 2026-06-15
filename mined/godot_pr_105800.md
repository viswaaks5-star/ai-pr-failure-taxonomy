# PR 105800 [MERGED] — [Web] Include emscripten headers by default
AUTHOR: adamscott

## BODY
Currently, developing using Emscripten for the Web platform is kinda a pain. As Emscripten uses by default it's own patched and new headers, the IDEs usually don't know what to do with Emscripten code because including manually those headers is not required.

<img width="792" alt="Capture d’écran, le 2025-04-26 à 13 59 12" src="https://github.com/user-attachments/assets/051ad4f1-67ad-4e4c-8afc-6f2c2e11240b" />

_This code compiles with Emscripten even if clangd complains._

~~So this PR adds a new option: `emscripten_include_path`. When added, this path will be included as an include path in the compilation.~~

_Edit:_ This PR now detects and adds the include path automatically, based on the detected binary.

<img width="696" alt="Capture d’écran, le 2025-04-26 à 14 09 15" src="https://github.com/user-attachments/assets/e5adaa7c-fa11-4437-8b0f-f9bfdf2da63e" />

_See how great it looks?_

> [!NOTE]
> **If you're using [emsdk](https://github.com/emscripten-core/emsdk):** 
> ~~`scons platform=web emscripten_include_path=<emsdk path>/upstream/emscripten/cache/sysroot/include`~~ (not needed anymore)
> 
> **If you're using directly [emscripten](https://github.com/emscripten-core/emscripten):**
> ~~`scons platform=web emscripten_include_path=<emscripten path>/cache/sysroot/include`~~ (not needed anymore)


## COMMENTS
--- dsnopek:
So, the goal is to get this include path into the `compile_commands.json`?

I wonder if there's a way to get Emscripten to give us the its include paths without the user having to specify them?

ChatGPT gave me this which seems to work:

```
emcc -v -E -x c++ - < /dev/null 2>&1 | awk '/#include <...> search starts here:/,/End of search list./ {if ($0 !~ /(#include|End of search)/) print $1}'
```

--- akien-mga:
Yeah I agree we should set this automatically and not require passing it on the command line.

A correct (current) Emscripten setup should have `EMSDK` in the environment I believe, so you can just append `$EMSDK/upstream/emscripten/cache/sysroot/include/` to `CPPPATH`.

--- adamscott:
> Yeah I agree we should set this automatically and not require passing it on the command line.
> 
> A correct (current) Emscripten setup should have `EMSDK` in the environment I believe, so you can just append `$EMSDK/upstream/emscripten/cache/sysroot/include/` to `CPPPATH`.

Not necessarily. You can setup it to work directly from the emscripten-core/emscripten repo.

--- akien-mga:
Thanks!


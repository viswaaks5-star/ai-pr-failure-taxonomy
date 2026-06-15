# PR 119168 [MERGED] — Add better error message when trying to decompress ZSTD with `decompress_dynamic`
AUTHOR: suhankins

## BODY
Right now, if you try to decompress ZSTD using `decompress_dynamic`, Godot will throw an error ```Condition "p_mode != MODE_DEFLATE && p_mode != MODE_GZIP" is true. Returning: (-1)```.

It's long, intimidating, and not obvious for developer what did they do wrong.

With this commit, trying to call `decompress_dynamic` with ZSTD compression will throw a more useful error `Dynamic decompression is only supported with gzip, DEFLATE, and Brotli compression methods.`

---

While documentation does mention that only gzip, DEFLATE, and Brotli are supported, it's possible that developer might not notice that, reuse existing code, or use code provided by an LLM.

## COMMENTS
--- Repiteo:
Needs rebase

--- suhankins:
> Needs rebase

Rebased

--- Repiteo:
Thanks!


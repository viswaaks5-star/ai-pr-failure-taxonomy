# PR 118494 [MERGED] — DDS: Use `put_u32` for unsigned writes.
AUTHOR: fire

## BODY
AI generated with Claude code.

@BlueCube3310 Can you check if this is a reasonable fix? The changes are small enough to review by hand.

UBSan reports:
  image_saver_dds.cpp:417: implicit conversion from type 'uint32_t'
  of value 4278190080 to type 'int32_t' changed the value to -16777216
  stream_peer.cpp:184: implicit conversion from type 'int32_t'
  of value -16777216 to type 'uint32_t' changed the value to 4278190080

The DDS pixel format masks (r/g/b/a_mask) are uint32_t but put_32 takes int32_t. Use put_u32 to avoid the round-trip conversion that UBSan flags when the high bit is set (e.g. a_mask = 0xFF000000).

This fix found a large class of uses where we put unsigned integer values into
integer puts.

## COMMENTS
--- fire:
I'll make an amendment to do all the uint initialized variables.

--- fire:
ahh I broke pr. will fix

--- fire:
The pull request is a lot more complicated now. Can you rereview?

--- fire:
I don't think I have enough time this weekend to check if it avoids breaking existing imports. So I'll leave it here. It's also salvagable.

--- BlueCube3310:
> I don't think I have enough time this weekend to check if it avoids breaking existing imports. So I'll leave it here. It's also salvagable.

This only touches the saver, not the loader. So imported files will not break. I'll test the changes soon, but they shouldn't cause any regressions since most of these types were unsigned ints anyway

--- Repiteo:
Thanks!


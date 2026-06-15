# PR 118495 [CLOSED] — csg: Fix signed-to-unsigned implicit conversions flagged by UBSan.
AUTHOR: fire

## BODY
AI generated with Claude code. The hope is that I can clean up the sanitation errors. These fixes are 2-3 lines so they can be verified easily.

UBSan reports:
  csg_shape.cpp:287: implicit conversion from type 'int' of value -1
  to type 'uint32_t' changed the value to 4294967295
  csg_shape.cpp:406: implicit conversion from type 'int' of value -1
  to type 'const unsigned int' changed the value to 4294967295

Use UINT32_MAX instead of -1 for the original_id sentinel and change faces_by_material to HashMap<int32_t, ...> to match Face::material.

## COMMENTS
--- fire:
I'll look into this more on my own.


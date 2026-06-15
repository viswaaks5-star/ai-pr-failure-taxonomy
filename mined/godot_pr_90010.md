# PR 90010 [CLOSED] — Optimize rendering_device `_add_dependency` and `_free_dependencies`
AUTHOR: Nazarwadim

## BODY
I removed unnecessary `has` checks that slow down `_add_dependency` and `_free_dependencies`. Added `PagedAllocator` for `dependency_map` and `reverse_dependency_map` as they can have 5000+ elements.

## COMMENTS
--- clayjohn:
Can you add a little bit more information about why this checks are not needed anymore?

--- Nazarwadim:
> Can you add a little bit more information about why this checks are not needed anymore?

In the `_add_dependency`, the `[]` operator automatically adds a new element.  `erase` also checks if a key exists in the table.

--- Nazarwadim:
@RandomShaper Can you take a look?

--- RandomShaper:
I guess this will be eventually supersed by #97016. Nonetheless, this is still worth considering before the other, more ambitious PR is assessed. My only remaining doubt is if the default page size of the allocators provides a reasonable tradeoff between allocation avoidance and memory overuse for this goal of tracking dependencies.

--- Nazarwadim:
Directly using the allocator in a map with many elements is better than using the default allocator, because the default has mutex overhead. But you are right that the default size of 4096 elements per page is too much. I think 1024 will be enough.
Edit: Asked ChatGPT and he said 126 - 256 would be a good value but I don't trust him so I'll use 512.

--- Calinou:
Do you have a test project where a bottleneck can be seen with the current approach? If so, please upload it :slightly_smiling_face: 

--- Nazarwadim:
@Calinou, no I don't have any. 


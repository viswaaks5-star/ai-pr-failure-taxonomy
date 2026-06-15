# PR 114794 [CLOSED] — Docs: Clarify that min() and max() require at least 2 arguments
AUTHOR: Clubhouse1661

## BODY
Fixes #114522

Clarifies the documentation for `min()` and `max()` functions to specify that they require at least 2 arguments, rather than the imprecise "any number of arguments" which could incorrectly suggest 0 or 1 arguments are valid.

- Updated `@GlobalScope.xml` to state both functions "take at least 2 arguments"

## COMMENTS
--- Clubhouse1661:
Thanks for the review. I agree that handling the single-argument case would be more intuitive, but that would be a behavior change rather than a documentation fix. 
Perhaps we should open a separate issue for it.

Otherwise, here's how we could add single-argument support:
`core/variant/variant_utility.cpp`

```cpp
Variant VariantUtilityFunctions::max(const Variant **p_args, int p_argcount, Callable::CallError &r_error) {
    if (p_argcount < 1) {  // Changed from < 2
        r_error.error = Callable::CallError::CALL_ERROR_TOO_FEW_ARGUMENTS;
        r_error.expected = 1;  // Changed from 2
        return Variant();
    }
    
    // Validate first argument type
    Variant::Type first_type = p_args[0]->get_type();
    if (first_type != Variant::INT && first_type != Variant::FLOAT) {
        r_error.error = Callable::CallError::CALL_ERROR_INVALID_ARGUMENT;
        r_error.argument = 0;
        r_error.expected = Variant::FLOAT;
        return Variant();
    }
    
    // Handle single-argument case
    if (p_argcount == 1) {
        r_error.error = Callable::CallError::CALL_OK;
        return *p_args[0];
    }
    
    // ... rest of existing logic unchanged
}
```


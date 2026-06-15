# PR 117800 [MERGED] — Add support for saving HDR screenshots to `Image.save_exr` functions.
AUTHOR: allenwp

## BODY
### What problem(s) does this PR solve?

- Fixes #117795

### What is the rationale for the approach used in this PR?

`Image.save_exr` functions have been modified to add two new parameters:
1. `color_image: bool`
   - Set `color_image` to `true` when saving a color image, such as a screenshot. Negative values will be included when `color_image` is `false`, which may be useful for saving raw floating point data such as a lightmap that includes negative light information.
   - When `true`, negative values are clipped to `0.0` to give correct colour rendering for screenshots.
3. `max_linear_value`
   -  Color component values in the resulting EXR file will not exceed `max_linear_value` if `max_linear_value` is not negative.
   - When saving screenshots of a project that uses HDR output, use `Window.get_output_max_linear_value` for `max_linear_value`.

**Clipping negative values (`color_image == true`)**

Internal to Godot, negative color values represent negative radiant energy for the purposes of lighting simulation. But for the purposes of CIE colorimetry, which is used for HDR image formats such as EXR, negative RGB values represent colors that are outside of the current RGB gamut and are positive RGB values in other color gamuts. For this reason, negative values should never be saved to EXR files that are intended to represent a color image such as a screenshot. This PR adds parameters to the existing `save_exr` and `save_exr_to_buffer` functions to allow saving of HDR screenshots.

**New `max_linear_value` parameter**

The new `max_linear_value` parameter matches [`Window.get_output_max_linear_value()`](https://docs.godotengine.org/en/latest/classes/class_window.html#class-window-method-get-output-max-linear-value). This means that producing an EXR image that is identical to the rendering presented by Godot is as simple as:

``` C++
get_window().get_texture().get_image().save_exr("screenshot.exr", false, get_window().get_output_max_linear_value())
```

With these changes, it is now possible to save an image that is identical to the image presented by HDR output:

<img width="1453" height="880" alt="image" src="https://github.com/user-attachments/assets/6f2d7486-3978-421f-ba08-1d372034ff0c" />

In the above renderings: the red, green, and blue rectangles shown on the bottom left corner contain negative values, such as those that may be created by negative lights. The colour sweep that comprises the majority of the render exceeds values of `1.0` on the right side.

### Was generative AI (LLM AI) used to create a portion of this PR?

No.

### Are there any parts of this PR that you are uncertain of or require special attention from reviewers?

- I haven't yet tested `SRC_FLOAT`. I don't know how to do this, but if it's possible to test this code path it should be done before merging. Anyone know how to?

## COMMENTS
--- Zylann:
> Negative values are clipped to 0.0 for existing save_exr and save_exr_to_buffer functions.

Isn't this going to break compatibility with uses such as saving floating point heightmaps? (i.e not colors). Those could contain legitimate negative values.


--- allenwp:
> > Negative values are clipped to 0.0 for existing save_exr and save_exr_to_buffer functions.
> 
> Isn't this going to break compatibility with uses such as saving floating point heightmaps? (i.e not colors). Those could contain legitimate negative values.

Yep. Good to know about that, thanks for pointing out this use case! Since I'll probably be looking into issues regarding use of wide gamut EXR files for skies/GI, I'm curious if you know of other times people may be saving and loading EXR with negative values. My suspicion is that EXR import of wide gamut colour images might play poorly with Godot lighting/rendering.

Presuming people have been using `save_exr` for non-colour data I guess this leaves these two options?

1. Introduce two new parameters instead of just one: `save_exr("path", "grayscale = false", "clip_negative = false", "max_linear_value = -1")`
2. Introduce a new function instead of changing the existing one: `save_exr_color_image("path", "grayscale = false",  "max_linear_value = -1")`

Option 2 sounds pretty dumb. With option 1, I could update the documentation to say that clip_negative should always be true when saving a colour image.

--- fire:
People using openexr for data would need to rescale to avoid losing data when -1 is clipped probably. I would expect some sort of non-default override for this.

Edited:

Adding a new function that does new things seems like the Reduz house-style.

--- allenwp:
Thanks again for the comment, @Zylann! Sometimes the urge to go back in time is too strong, but maintaining compatibility is paramount.

I've reworked this PR to maintain existing behaviour and it is now ready (again) for review.

--- Repiteo:
Thanks!


# PR 115688 [CLOSED] — jpg: Add quick and dirty conversion of CMYK/YCCK colorspaces to RGB
AUTHOR: akien-mga

## BODY
This relies on a helper function from TurboJPEG which is labeled as quick and dirty and for testing purposes.

It might be good enough for badly prepared game assets (e.g. JPGs downloaded from the web) and better than outright failing.

- Fixes #115668.
- Alternative to #115674.

<img width="1354" height="628" alt="image" src="https://github.com/user-attachments/assets/5b243cb5-8408-471c-9f8b-d9fe851a463c" />

---

### AI disclosure

This was partially coded with the help of AI agents. I first used ChatGPT (GPT-5.2) to rubberduck the issue, which utterly failed at providing me code that would actually work, but helped me understand the problem space better.

I also read some of TurboJPEG's code myself and found its `cmyk.h` helper functions, though I didn't go in depth to see how it's being used exactly (there's several levels of abstraction and a mix between TJ and jpeglib APIs which makes it a bit convoluted).

Then I fed this initial research to Copilot in VS Code with access to my local Git clone (GPT-5 mini), and it came up with a working branch for CMYK, which I tested to fix support for the file in #115668.

Vibe coding like this isn't something I intend to do frequently, but I was mostly curious to see how well it would work for something pretty "standard" like this. I have mixed feelings, but did get a working solution.

The final code was edited by me and is pretty much how I would have written this if I was already familiar with TurboJPEG. I don't believe these few lines of effective code pose any copyright challenge.

### Notes

- I still need to test the conversion for YCCK because this is mostly something Copilot took from ChatGPT's bad code, and I need to validate that it's actually correct.
- Would be good to test more complex CMYK files (photos, etc.) and see if the quick and dirty conversion does yield good enough results.
- It could be good to let users know that they imported CMYK/YCCK files and that we recommend converting them properly to RGB colorspace, so we don't rely on our subpar conversion. I could put a `print_verbose` where it detects CMYK/YCCK, but at this point we only have a buffer so no file name to give. Passing it to the calling site as a new function argument feels a bit dirty.

## COMMENTS
--- akien-mga:
> I still need to test the conversion for YCCK because this is mostly something Copilot took from ChatGPT's bad code, and I need to validate that it's actually correct.

Heh, quick try with https://en.wikipedia.org/wiki/File:Channel_digital_image_CMYK_color.jpg

Result:
<img width="591" height="396" alt="image" src="https://github.com/user-attachments/assets/829b0674-5b23-4467-bf45-86d64a22ff7d" />

We're not there yet.

*Edit:* Looking closer at TurboJPEG, they don't seem to do additional inversion for YCCK. Removing it seems to solve the issue.

<img width="546" height="382" alt="image" src="https://github.com/user-attachments/assets/5192a9c7-62d8-46a3-8b40-1b54477cc2d1" />

Comparison between the original YCCK and the RGB8 conversion: https://imgsli.com/NDQ2Nzgw
Seems pretty good to me. There's some extra compression artifacts (resaving as JPEG is lossy and I didn't tweak quality) but colors seem the same to me.

--- puzzlepiece87:
@akien-mga @bruvzg Is there more that needs to be done for this to be approved, or is it just waiting in queue to be part of the next release?

--- fire:
As far as I know, no one really is in this area. So it's hard to find reviewers. @allenwp did the HDR work and has some experience with colour spaces.

--- allenwp:
Thanks for the ping, fire!

> It might be good enough for badly prepared game assets (e.g. JPGs downloaded from the web) and better than outright failing.

I'm uncertain why this is better than failing. My gut tells me that failing is better because a warning may be missed by the user and the result of this conversion is likely not what the user desires...

Which brings me to my next question: what is the user actually expecting (exactly)? Is there a proposal that describes why a user is not able to convert their image to sRGB before importing? CMYK to sRGB conversion is a complicated thing to do well.

My expectation is that a user may have designed artwork or graphics for print media, say in Adobe Photoshop or similar. This artwork was saved as a CMYK jpeg for print usage. This user may want to directly present these images in Godot, so they import the CMYK jpeg straight into Godot and find that colours are different in Godot than what they saw when they printed the image or when they previewed the CMYK jpeg in Photoshop. Here is an example of Photoshop's rendering compared to this PR's rendering:

<img width="672" height="302" alt="image" src="https://github.com/user-attachments/assets/6b0c3de4-107b-4181-9d40-1e0caed395a9" />

(The left side is Godot rendering, the right side is Photoshop)

Some of the colours are similar, but the blues are especially different.

I expect that chasing good CMYK to sRGB conversion is something not worth doing: this is an especially difficult process that is best left to image editing tools that have taken on the difficult challenge.

--- puzzlepiece87:
> Is there a proposal that describes why a user is not able to convert their image to sRGB before importing?

My use case is using capsule images from a user's Steam library games to show their achievements by genre in comparison to their friends:
https://media.discordapp.net/attachments/769986651647770634/1413423017761046578/image.png?ex=698adbc3&is=69898a43&hm=80552465c6a0531ae32025997af513266439d960463079425dd52c5543388ef8&=&format=webp&quality=lossless&width=1175&height=633

Museum of all things uses images from Wikipedia to create an infinite 3d museum (though their specific issue was solved by an earlier PR)
https://github.com/m4ym4y/museum-of-all-things/issues/56

I am not sure what Tripp-Sautner's use case was; they were also using images from Steam.
https://github.com/godotengine/godot/issues/45523#issuecomment-3726981219

--- akien-mga:
Yeah the use case is basically streaming media you don't control / UGC, where it's probably preferred to load the image with small color differences than outright fail (especially if the game developer doesn't control which JPG file will be downloaded and doesn't expect any of them to use CMYK and doesn't properly handle it - which our API doesn't really let you do either).

But on the other hand that's why it would be useful to still flag those assets as not well supported by Godot, for use cases where it's not streamed media / UGC but actually first party assets, because then the game developer should convert them to RGB with PhotoShop / ImageMagick.

--- allenwp:
Ah, this was not clear to me that this is specifically about supporting downloading arbitrary jpg images at runtime that may be user generated and/or entirely outside of the game developer's control! (I read this PR's text and the main issue description of the [linked bug](https://github.com/godotengine/godot/issues/115668#issue-3878734620), but didn't read through all of the related comments and other linked issues.)

> But on the other hand that's why it would be useful to still flag those assets as not well supported by Godot, for use cases where it's not streamed media / UGC but actually first party assets, because then the game developer should convert them to RGB with PhotoShop / ImageMagick.

Yes, this sounds like a reasonable approach. I'd make it as in-your-face as possible, because the use case for this is not for any jpg files inside of your `res://`, but instead just for doing a better-than-nothing interpretation of downloaded files that are out of your control.

...Maybe it would be better to limit this hacky CMYK jpeg support to `image.LoadJpgFromBuffer(...)` ? Or maybe that would overcomplicate things.

Either way, I'd say the colour interpretation of this PR is not suitable for files that the game developer has control over so it should give an error messages saying "Color may not be rendered correctly. Please re-save this file as an RGB image." or just fail altogether if they try and put a CMYK jpeg in their `res://`. It should be very clear to the game developer that there is something wrong with this jpeg file, as it is not designed to be displayed on screens, but instead should only be used for print media.

--- akien-mga:
I don't have time to work on this further for now, so let's go with rejecting this colorspace for now: #115674.

I think a "best effort" conversion like done here could still be useful, but indeed it should only be used for UGC and not something developers rely on for their own assets, as it's much better for those to convert them properly to RGB.
This would require some core changes which might be a bit confusing or tricky so it's proposal material.


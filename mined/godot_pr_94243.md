# PR 94243 [MERGED] — Fix Image CowData crash when baking large lightmaps
AUTHOR: Calinou

## BODY
This switches to 64-bit integers in select locations of the Image class, so that image resolutions of 16384×16384 (used by lightmap texture arrays) can be used properly. Values that are larger should also work (the Image class' `MAX_PIXELS` constant is `2^28` pixels, and `2^24` pixels on each axis).

VRAM compression is also supported, although most VRAM-compressed formats are limited to individual slices of 16384×16384. WebP is limited to 16383×16383 due to format limitations.

Note that very large lightmaps will cause the scene to load significant slower – this would be addressed by using VRAM compression, but it's currently very slow on lightmaps this large. https://github.com/godotengine/godot/pull/91535 should make compression times more reasonable, but I haven't tested it together with this PR yet. https://github.com/godotengine/godot/pull/50574 can also help bring down file sizes and memory usage (and could be coupled with VRAM compression for further gains).

Please test this on your own projects :slightly_smiling_face: 

cc @jcostello @BlueCube3310 @SpockBauru @jitspoe @TokisanGames @DarioSamo

PS: How do we handle GDExtension compatibility on this one? Is it possible to add a compatibility method in this case?

```
Error: Validate extension JSON: Error: Field 'classes/Image/methods/get_mipmap_offset/return_value': meta changed value in new API, from "int32" to "int64".
```

- This closes https://github.com/godotengine/godot/issues/54679.

**Testing project:** [global_illumination_updated.zip](https://github.com/user-attachments/files/16184863/global_illumination_updated.zip)
*Previously, this project would crash upon baking lightmaps. It works now.*

## Preview

![Lightmap editor](https://github.com/user-attachments/assets/e3f9864d-418a-46b6-b9b1-04d865b29ac0)

## COMMENTS
--- reduz:
@RandomShaper Since you are here, I think these have to be fixed too, as some return size or offset in uint32_t (my fault).

Like this:
https://github.com/godotengine/godot/blob/97b8ad1af0f2b4a216f6f1263bef4fbc69e56c7b/servers/rendering/rendering_device_commons.h#L860

--- passivestar:
@Calinou the provided test project has glb with the default texel size of `0.1` and LightmapGI texel scale is also the default value `1`. Not knowing what large value to change it to for testing I set it to `30` and it immediately crashed the editor when I clicked bake :D
```
MTLTextureDescriptorInternal validateWithDevice:]:1357: failed assertion Texture Descriptor Validation
MTLTextureDescriptor has width (210870) greater than the maximum allowed size of 16384.
MTLTextureDescriptor has height (278700) greater than the maximum allowed size of 16384.
```

--- Saul2022:
> what large value to change it to for testing I set it to `30` and it immediately crashed the editor when I clicked bake :D

It might be the file size and the fact it still really slpw for the m1 max to handle. 


> MTLTextureDescriptor has height (278700) greater than the maximum allowed size of 16384.


Why is it so big  lol...


--- jcostello:
Im getting this error baking sponza with texel density set to `3`

```
 Too many pixels for Image. Maximum is 16777216x16777216 = 268435456pixels.
  core/io/image.cpp:2798 - Condition "dsize == 0" is true.
```


--- SpockBauru:
Built @Calinou's repo locally and made a test with my LightmapProbeGrid plugin demo scene. I enabled lightmap only for the terrain (disabled for the tunnel, trees, etc.).

Here the test project, you may have to restart on the first launch because the probes plugin:

[LightmapProbeGrid.zip](https://github.com/user-attachments/files/16195658/LightmapProbeGrid.zip)

There are 2 modified scenes on this test: the Demo Scene (main scene) and the Terrain scene (GLTF inherited scene).

On the Terrain scene, unwrapping the terrain's UV2 in Godot generates a Lightmap Size Hint of 12034x12238 (the terrain is not perfectly squared) which is bellow the 16384 max size from this PR.

Back to the demo scene if I bake the LightmapGI it results in a wall or errors with a pitch-black terrain and the lightmap .exr file is also full black. The same happen lowering the resolution all way down to 8192 (2^13):

![image](https://github.com/user-attachments/assets/8fc9943d-772e-4b54-bd25-4b70c8af27cc)

![image](https://github.com/user-attachments/assets/666d3cb8-770d-4d55-96ad-ad90452dfe32)


By reducing the Lightmap Size Hint to 8053x8190, it freezes the editor on `Determining optimal atlas size`:
![image](https://github.com/user-attachments/assets/81f35952-3857-44a8-8cb4-ee4118f08a86)

![image](https://github.com/user-attachments/assets/68230c7c-fe1b-4e55-a58e-79ac186292bb)

With the resolution of 8023x8139, it bakes normally without errors. The resulting EXR file has a resolution of 8192x8192
![image](https://github.com/user-attachments/assets/309a3246-3296-4a2a-b03c-6e2d7f401195)

![image](https://github.com/user-attachments/assets/04e3019a-dd0b-4a1e-9928-033ba3372cc9)

In a short: Any attempt on creating a Lightmap file with resolution above 8192 didn't work on this demo :'(

Edit: 
System info: `Godot v4.3.beta unknown - Windows 10.0.22631 - Vulkan (Forward+) - dedicated NVIDIA GeForce RTX 3080 (NVIDIA; 32.0.15.5612) - 12th Gen Intel(R) Core(TM) i7-12700KF (20 Threads), 32GB RAM`

--- BlueCube3310:
> By reducing the Lightmap Size Hint to 8053x8190, it freezes the editor on `Determining optimal atlas size

Could you try rebasing this on top of #94237?

--- SpockBauru:
> > By reducing the Lightmap Size Hint to 8053x8190, it freezes the editor on `Determining optimal atlas size
> 
> Could you try rebasing this on top of #94237?

Sorry, I can't... I don't have enough knowledge to rabase one PR in another one :'(

Edit: Testing the Windows artifact of #94237, it crashes the editor when defining the Lightmap Size Hint to 8053x8190

--- BlueCube3310:
After adding the patches from that PR 16k lightmaps bake correctly. The first case seems to happen when the generated atlas is rounded to 32k, though I'm not certain about that yet.

--- Calinou:
Very few GPUs support 32768x32768 textures and their memory usage is obscene, so the lightmapper should clamp the size down in that case (and print a warning advising the user to reduce their texel scale property).

Textures should already not exceed 4096x4096 in the first place if you want them to show up reliably on mobile/web platforms (they could be shrunk on export).

--- lyuma:
> the lightmapper should clamp the size down in that case (and print a warning advising the user to reduce their texel scale property).

The entire underlying issue here is a UX problem and lack of communication with the user.

i doubt I have ever *wanted* godot to create even a 16k lightmap texture. It is still better to not crash, but we certainly shouldn't make it possible to go higher.

> Textures should already not exceed 4096x4096 in the first place if you want them to show up reliably on mobile/web platforms 

Indeed, this is the real problem. I think Godot needs better UX here to show the user what size texture would be generated, explain the consequences with mobile and web support, diagnose which meshes are responsible for the bloated size, and give the user various options to keep the lightmap within the size budget the user asks for.

It might be nice to have a max lightmap size option and perhaps options like "downscale" or "error" if it goes over that size budget. (The problem is usually one mesh is taking way more space in the lightmap, and it might be a relatively unimportant object or have very little detail, so if I knew which it is then I could adjust the settings)

--- jcostello:
@lyuma sorry my ignorance, but is there a limit of how big a scene can be (because of the texture size) or the problem is the texel density?

--- Saul2022:
> > the lightmapper should clamp the size down in that case (and print a warning advising the user to reduce their texel scale property).


Agreeed, even ue5 being  pretty high end  might just support 8k texture at  maximum here.

<img alt="Screenshot_20240714_053655_Chrome" src="https://github.com/user-attachments/assets/cdf7d258-2f84-4771-8842-700c78bfe671" width="360">



--- lyuma:
We tend to discourage posting AI responses because of its tendency to be verbose or inaccurate: the AI generated response is wrong. UE4's resolution limit of 8192 is likely no longer present at least in UE 5.1, (and UE 5.x in particular may be able to make use of virtual texturing in some cases to go beyond conventional resolution limits)

That said, UE5 docs contain this warning:
> "Some GPUs have hardware limits in the maximum size texture they can support. For example, some GPUs may not support texture sizes larger than 8192 pixels (8k)."

my guess is most desktop GPUs support 16k (supposedly GPUs without support for 16k will be DX10 only). Still, relying on 16k textures might make your content inaccessible to mobile users or old/low-end desktop hardware.

That said, while an uncompressed 16k HDR lightmap texture will take 2 Gigabytes of contiguous memory which would be impractical on most GPUs, BPTC should be able to cut that down to 8bpp, only 256MB of memory, which should be acceptable.

--- SpockBauru:
I believe the main issue is not the lightmap size, but the lack of automatic lightmap tiling where lightmaps are splitted in chunks.

In Unity you can set the max size of each tile and several are automatically generated according the need. The engine bakes one by one so gpus with low amount of memory can bake big scenes without issues. Tiles have not a fixed size, but rather vary according the region, each tile with its own file.

For Godot we can take a step further and after baking make the game load/unload each tile as needed, but how to make it must be a topic of careful discussion since is far from trivial.

Since Godot aims to include low end platforms and also simplify the development as much as possible, I believe that a fully automatic tiling system without the need for user interaction would be the best approach for developing games with relative big maps, not only full open worlds but also things like a racing game with 10km tracks, or something like the Gran Pulse level on Final Fantasy XIII.

--- Calinou:
> For Godot we can take a step further and after baking make the game load/unload each tile as needed, but how to make it must be a topic of careful discussion since is far from trivial.

Mesh splitting is needed to get decent culling (and already has its own [proposal](https://github.com/godotengine/godot-proposals/issues/3673)), but it's difficult to do right in a way that preserves materials and both UV layers.

--- SpockBauru:
> Mesh splitting is needed to get decent culling (and already has its own [proposal](https://github.com/godotengine/godot-proposals/issues/3673)), but it's difficult to do right in a way that preserves materials and both UV layers.

As far as I remember, Unity does not perform mesh splitting on the lightmaps, it only groups whole meshes.

 Instead, the user defines the max size of the lightmap tile and if a mesh exceeds that, the lightmap resolution of the mesh is automatically shrunk to fit the max size. After baking a warning is print in the console.


Example:

If a terrain with 1km² have defined 4 samples per meter, it would not fit an 1024x1024 lightmap tile. In this case the engine automatically shrinks the terrain lightmap resolution to fit the max tile size. 

After that, the bake is done normally and give a console warning telling the user what objects had their lightmap resolution reduced.




--- Saul2022:
Prob or we could do what unreal does as making the lightmap a texture atlas( idk if it’s done already, but it’s an idea for file sizes). As for resolution  i agree with lyuma  about limit prob being 15k since with this and bluecibe performance it does seem to improve the situatuon, though i would say an resolution limit option  should be brought in. 

--- BlueCube3310:
The other compression modes (ASTC, CVTT, etcpak) should probably be adjusted for this as well, even though compressed images technically shouldn't require 64-bit offsets/sizes.

--- akien-mga:
Rebased and updated the PR to fix the image unit tests.

I confirm this fixes the MRP in the OP.

I also removed `int Image::get_mipmap_byte_size(int p_mipmap) const` which wasn't used anywhere (its only used was in 4 years old `#if 0`'d code, which I removed too).

And added a compat binding for `get_mipmap_offset` which is exposed to scripting.

> The other compression modes (ASTC, CVTT, etcpak) should probably be adjusted for this as well, even though compressed images technically shouldn't require 64-bit offsets/sizes.

I guess we can merge this PR first and either @BlueCube3310 or @Calinou can do this as a follow-up?

--- akien-mga:
Thanks!

--- SpockBauru:
Downloaded the windows artifact and simplified the terrain scene to include only the needed parts. Now we can simply set the lightmap_size_hint on the Terrain Mesh node to get the desired lightmap file size after baking.

Terrain test scene:

[TerrainLightmapTest.zip](https://github.com/user-attachments/files/16314203/TerrainLightmapTest.zip)


I agree that this PR can be merged as it is, and a follow up will be needed.

The artifact can correctly generate Lightmap files up to 8192, which is better than we had, but between this value and the proposed 16384 it still generates a black lightmap file with a wall of errors.

May I be tagged on the follow up PR to test this issue? ^-^



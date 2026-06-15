# PR 102552 [MERGED] — Add shader baker to project exporter.
AUTHOR: DarioSamo

## BODY
## Overview

Based mostly on the work done by @RandomShaper, this PR adds a new Editor Export Plugin that will scan resources and scenes for shaders and pre-compile them on the right format used by the driver in the target platform.

Shaders on SPIR-V, DXIL and MIL formats are interchangeable between systems and can be shared to end-users to skip long startup times resulting from having to compile them on the target platform. While pipeline compilation is still unavoidable and a requirement, Godot is currently and unnecessarily doing work on the end user's system that can be done ahead of time in the Editor and shipped as part of the final project.

This PR required a large amount of work on refactoring the Shader classes and decoupling the Shader Compilers from the Rendering Device Drivers we currently have. A new generic Shader Container class has been introduced and allows for heavy customization of the exported shader if required by the target platform. A significant amount of work has gone into also taking out any platform-specific definitions that were being added to shaders that may differ in the end user's system, and in the cases this is unavoidable for optimization reasons, shader variants have been created instead.

When using this PR, Shader Baking is an optional step that will increase the export time of a project with the major benefit that the end user who plays the game will be able to skip shader compilation entirely.

![image](https://github.com/user-attachments/assets/81917527-c2af-4219-b793-a286d444a1b5)

Another important change is the ability for the Shader class to use a multi-level shader cache: one that it reads and writes from as regular and one it can use as the fallback and is read-only. This one is filled in with the directory from the exported project's embedded shader cache in the .pck.

This feature is intended to be finished for Godot 4.5 if possible.

## Results

The results speak for themselves when dealing with backends that have very long shader conversion times. While in Vulkan the improvement is there but not as noticeable on a system with many threads, the difference is astounding when dealing with a backend like D3D12, which has very long conversion times due to the NIR transpilation process.

**Even on a system with 32 threads, a D3D12 project goes from taking over a minute to load to just ~2 seconds.**

TPS demo using D3D12 backend without and with using the shader baker functionality.

`master`

https://github.com/user-attachments/assets/00f9a39c-7101-41c6-b5b1-139b9df165ea

`shader-baker`

https://github.com/user-attachments/assets/956be00e-f5ae-488d-8ff4-354c46e7068d

The results are reproducible but not as drastic on Vulkan, although you'll gain the biggest benefit out of this feature the less CPU threads you have at your disposal.

Notice that for testing this effectively, you must **delete the shader_cache present in the user directory for the project you're testing**, as between runs, Godot will cache compiled shader binaries in this directory. On Windows, this directory can be found in `%AppData%/Godot/app_userdata/<Project Name>/shader_cache`.

## TODO
- [x] Metal support (@stuartcarnie has shown interest in tackling this).
- [x] Verify how this can interact with imported GLSL files.
- [x] Find and account for more edge cases the shader baker is not catching currently by testing on a wider variety of projects.
- [x] Account for the cases where the renderer must be set to the matching renderer of the exported platform for embedded shaders to be baked. Warn appropriately on the editor.
- [x] Verify there's no regression in BaseMaterial3D being updated automatically in the viewport from a user editing it.
- [x] Find the remaining global shader defines that might be around the codebase from querying the current rendering device's capabilities.
- [x] Check this project (https://github.com/godotengine/godot/pull/102552#issuecomment-2787924534).
- [x] Check multiview support.
- [x] Add renderer as part of the hash.
- [x] See if it's possible to improve the progress bar feedback.
- [x] Add project export warning when renderer doesn't match the renderer forced for the platform being exported.
- [x] Make IntegrateDfgShaderRD not delete itself after creation.

_Bugsquad edit: Should fix: https://github.com/godotengine/godot/issues/94734_

---

Contributed by [W4 Games](https://w4games.com/). 🍀

## COMMENTS
--- stuartcarnie:
This is great! 

Will you merge to the main branch, and then I can follow up with a PR to implement Metal support? 

If the user is on Windows or macOS, we can utilise the Metal compiler toolchain to generate Metal libraries, reducing load times even more, as that compiles the Metal source into a platform-independent, intermediate format. I notice that [Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-the-windows-metal-shader-compiler-for-ios-in-unreal-engine) has an option to do this.

--- DarioSamo:
> Will you merge to the main branch, and then I can follow up with a PR to implement Metal support?

I think it's pretty far from being merged to main at the moment due to 4.4 going into RC soon, I think it'd be best to just PR to this branch as I don't think it'll take too long to adapt what we have to it.

> If the user is on Windows or macOS, we can utilise the Metal compiler toolchain to generate Metal libraries, reducing load times even more, as that compiles the Metal source into a platform-independent, intermediate format. I notice that [Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-the-windows-metal-shader-compiler-for-ios-in-unreal-engine) has an option to do this.

Yes, this would be great. There's a scheme for adding "Platforms" and you can definitely do a Windows-specific version that loads the toolchain if you're under Windows to produce the MIL instead.

Under the new Shader Container design, you won't need to handle anything about serialization of the Shader reflection. All you need is to just convert to the shader binary and you can insert whatever extra bytes you wish to serialize that the platform might need.

--- warriormaster12:
Will this feature bake shaders for all backends by default? If yes, can users filter out certain backends out of the export process? Say if developers decide to support Vulkan only on a platform that supports Vulkan and Dx12.

--- DarioSamo:
> Will this feature bake shaders for all backends by default? If yes, can users filter out certain backends out of the export process? Say if developers decide to support Vulkan only on a platform that supports Vulkan and Dx12.

It bakes the shaders for the driver selected for the platform. It doesn't cover the case at the moment of the user offering options for multiple backends.

--- Calinou:
One concern I have is for users exporting to Windows from Linux (which is a common scenario on CI). While it should be possible to export SPIR-V already for projects using Vulkan, exporting DXIL for Direct3D doesn't sound feasible right now. None of the D3D12 code is compiled in the Linux editor which is used for exporting on CI. This also applies to users exporting for macOS from other platforms.

Of course, you can sidestep this by using a Windows CI runner, but these are generally slower to perform a full CI run due to slower I/O (and may have higher demand too, leading to increased queues).

More generally, I don't know if this shader compilation process will work in headless anyway (since no GPU is initialized, and none is available on GitHub Actions unless you pay for it).

I suppose we'd need a way to build the NIR stuff regardless of whether Direct3D 12 is enabled in the current build, as long as it's an editor build.

--- DarioSamo:
> One concern I have is for users exporting to Windows from Linux (which is a common scenario on CI). While it should be possible to export SPIR-V already for projects using Vulkan, exporting DXIL for Direct3D doesn't sound feasible right now. None of the D3D12 code is compiled in the Linux editor which is used for exporting on CI. This also applies to users exporting for macOS from other platforms.

The only D3D12 code that is required at the moment is root signature serialization to a binary blob. If that can be worked around (CC @RandomShaper), then D3D12 is not a requirement for building D3D12 shaders.

> More generally, I don't know if this shader compilation process will work in headless anyway (since no GPU is initialized, and none is available on GitHub Actions unless you pay for it).

The shader classes aren't tied to a particular driver running. No GPU is required for the process, as that was part of most of the refactoring that was done to take it out of the drivers and into their own classes that can be used independently.


--- TCROC:
@Calinou Just brought this PR to my attention!  I am super excited to test this out!  Please feel free to @ me when this is ready to be tested :)

--- kisg:
Would it be possible to schedule this to 4.5? What would be required to do so?

--- DarioSamo:
> Would it be possible to schedule this to 4.5? What would be required to do so?

Metal's the only component missing as far as I can tell. I can get around to it by the time we enter 4.5 but I'd like to give Stuart time to see if he can manage it as he's more familiar with the driver than I am.

--- stuartcarnie:
@DarioSamo do you think you could merge to the main branch once 4.4 is release, so I can work from my fork with my build configuration? I will be able to implement it fairly easily from there.

--- DarioSamo:
> @DarioSamo do you think you could merge to the main branch once 4.4 is release, so I can work from my fork with my build configuration? I will be able to implement it fairly easily from there.

I'm not sure it's possible as I can't figure out a way that isn't very cumbersome to have the current scheme and the new scheme working in tandem without, in the process, just adapting the Metal backend to use the new shader container format and basically ending up with a working shader baker most of the way there already.

--- TCROC:
@stuartcarnie @DarioSamo 

I'm actually confused by both the question and the answer.

> do you think you could merge to the main branch once 4.4 is release, so I can work from my fork with my build configuration? I will be able to implement it fairly easily from there.

Aren't all PRs merged into the main branch?

> I'm not sure it's possible as I can't figure out a way that isn't very cumbersome to have the current scheme and the new scheme working in tandem without, in the process, just adapting the Metal backend to use the new shader container format and basically ending up with a working shader baker most of the way there already.

Same reason for confusion.  Why wouldn't it be possible?  Aren't all PRs merged into the main branch?  In fact, isn't this PR explicitly requesting to merge into master?

Thank you! :)

--- TCROC:
Oh I think I see what you are asking now.  This branch has merge conflicts.  Are you asking if these can be resolved?

--- DarioSamo:
@TCROC It's not the merge conflicts, it's the fact that Metal does not build at the moment on this PR. It can't be merged as it breaks the platform. I don't have an easy way to not break it as the changes are fundamental to how the shader methods work. 

The amount of work to make it build as a bandaid fix would be roughly equivalent to the amount of work to implement the shader container in Metal that is necessary for shader baking to work.

--- TCROC:
Ah I see.  Thank you for the explanation! :)

--- stuartcarnie:
👋🏻 @kisg 

# Overview: Metal

Currently, we use SPIRV-Cross to generate Metal Shader Language (MSL) from the SPIR-V and serialise this source to the binary data. We want to be able to support using the offline Metal compiler toolchain so that we can generate a `.metallib` file, when the toolchain is available. It isn't required, but will further reduce startup time, as devices such as iOS won't have to execute the Metal Compiler background task to compile the MSL first.

# Solution Sketch: Metal

To support MSL and .metallib, we should extend `ShaderBinaryData`:

https://github.com/godotengine/godot/blob/5312811c4da268892087a88d2b5cdc716f2c219e/drivers/metal/rendering_device_driver_metal.mm#L1557

and a `library_type` field, that is an enumeration:

```cpp
enum LibraryType {
  METAL_SHADER_LANGUAGE,
  METAL_LIBRARY,
}
```

> [!NOTE]
>
> Adding a field will require the version is updated:
>
> https://github.com/godotengine/godot/blob/5312811c4da268892087a88d2b5cdc716f2c219e/drivers/metal/rendering_device_driver_metal.mm#L1076

The remainder of the work is just implementing the container, as @DarioSamo has done for Vulkan and D3D12. _Don't worry about implementing offline compilation for your initial PR_


# Offline compilation

Offline compilation takes the MSL and create a `.metallib`. See [this page](https://developer.apple.com/documentation/metal/building-a-shader-library-by-precompiling-source-files?language=objc) for more information.

Future work will add support to spawn the Metal compiler toolchain, which is available for macOS and Window platforms, and generate `.metallib` files. We can serialise these instead of the raw MSL. Instead of creating a `MTLLibrary` from source:

https://github.com/godotengine/godot/blob/9fc39ae321ffd8feb7032f090f63e232006a55f6/drivers/metal/metal_objects.mm#L2028-L2044

which results in background compilation, we can use the [`newLibraryWithData:error:`](https://developer.apple.com/documentation/metal/mtldevice/makelibrary(data:)?language=objc) API to load a compiled Metal library.



--- stuartcarnie:
@DarioSamo when we're baking shaders, do you think it might be possible to provide the parameters required to generate a pipeline state descriptor?

@kisg I suggest you watch [this Apple developer video](https://developer.apple.com/videos/play/wwdc2022/10102), as it is possible we could provide a 3rd level of compilation, to completely remove runtime compilation. We would need the pipeline descriptor state to achieve this deeper level of customisation, but that would have to come from Godot so we could generate the appropriate JSON descriptor.

--- kisg:
FYI:

We have a working Metal implementation of the Shader Baker. It supports both runtime (where we bake the MSL source code) and offline Metal compilation. The offline compilation generates the platform independent bytecode (AIR) format. 

In our test application the MSL baking did not make much difference, but with the AIR baking the first startup time went from ~ 7+ seconds to ~2 - 2.5 seconds. The same app with Vulkan (with Shader Baker enabled, so SPIR-V baked in the app) + MoltenVK starts in ~5.1 seconds.

We have to clean it up a bit (currently it only supports iOS targets, no MacOS), but we hope to publish it soon as a PR for this PR.

--- TCROC:
Brilliant! Great work @kisg! I look forward to testing it out! :)

--- DarioSamo:
@kisg Awesome to hear! I'll be glad to review and merge it once it's done!

--- stuartcarnie:
@kisg awesome to hear – I'll be happy to help review it when ready too!

--- stuartcarnie:
> In our test application the MSL baking did not make much difference, but with the AIR baking the first startup time went from ~ 7+ seconds to ~2 - 2.5 seconds. The same app with Vulkan (with Shader Baker enabled, so SPIR-V baked in the app) + MoltenVK starts in ~5.1 seconds.

@kisg Great stuff! Were you using the `LAZY` shader initialisation when testing the baking to MSL?

--- kisg:
> > In our test application the MSL baking did not make much difference, but with the AIR baking the first startup time went from ~ 7+ seconds to ~2 - 2.5 seconds. The same app with Vulkan (with Shader Baker enabled, so SPIR-V baked in the app) + MoltenVK starts in ~5.1 seconds.
> 
> @kisg Great stuff! Were you using the `LAZY` shader initialisation when testing the baking to MSL?

Yes, we have it hardcoded to LAZY for the MSL based cache now. :) 

--- stuartcarnie:
That is going to be a very nice win!

Another feature we might be able to use in the future is `MTLBinaryArchive` to save compiled pipelines for future use. That is an area I'm going to explore more in the future. I am not sure yet if it will eliminate the requirement to compile the `MTLLibrary`, as `MTLBinaryArchive` is specified when creating the Metal pipeline.

--- akien-mga:
> FYI:
> 
> We have a working Metal implementation of the Shader Baker. It supports both runtime (where we bake the MSL source code) and offline Metal compilation. The offline compilation generates the platform independent bytecode (AIR) format.
> 
> In our test application the MSL baking did not make much difference, but with the AIR baking the first startup time went from ~ 7+ seconds to ~2 - 2.5 seconds. The same app with Vulkan (with Shader Baker enabled, so SPIR-V baked in the app) + MoltenVK starts in ~5.1 seconds.
> 
> We have to clean it up a bit (currently it only supports iOS targets, no MacOS), but we hope to publish it soon as a PR for this PR.

Hi @kisg - what's the status on your Metal implementation? We'd like to get the shader baker merge sooner than later in the dev branch for 4.5, so we don't risk missing the merge window, and get enough testing before the stable release.

--- kisg:

> Hi @kisg - what's the status on your Metal implementation? We'd like to get the shader baker merge sooner than later in the dev branch for 4.5, so we don't risk missing the merge window, and get enough testing before the stable release.

We will provide a PR for this PR this week; sorry for the delay.


--- kisg:
@DarioSamo Would it be possible to rebase this PR on the current master before I create the Metal PR?

--- DarioSamo:
> @DarioSamo Would it be possible to rebase this PR on the current master before I create the Metal PR?

It might take some work but I'll see to get it done this week if possible.

--- DarioSamo:
@kisg Rebased on top of the latest master.

--- clayjohn:
@kisg Now that it is rebased, what is your timeline for making a PR?

--- kisg:
> @kisg Now that it is rebased, what is your timeline for making a PR?

Just opened the PR in @DarioSamo's repository: https://github.com/DarioSamo/godot/pull/2

Or can I open it here against this PR?

--- DarioSamo:
> Just opened the PR in @DarioSamo's repository: [DarioSamo#2](https://github.com/DarioSamo/godot/pull/2)
> 
> Or can I open it here against this PR?

That should be fine. Thanks! CC @stuartcarnie 

--- ghuser404:
I tried this branch with d3d12 renderer and I'm getting this
![image](https://github.com/user-attachments/assets/1b2f24d1-9ab7-4ee0-b2c6-974a9ed7bcfe)


--- ghuser404:
Also, is it possible to do the baking on a thread, not to freeze the UI?

--- DarioSamo:
> I tried this branch with d3d12 renderer and I'm getting this ![image](https://private-user-images.githubusercontent.com/33043976/431598894-1b2f24d1-9ab7-4ee0-b2c6-974a9ed7bcfe.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDQxNTUyNzcsIm5iZiI6MTc0NDE1NDk3NywicGF0aCI6Ii8zMzA0Mzk3Ni80MzE1OTg4OTQtMWIyZjI0ZDEtOWFiNy00ZWUwLWIyYzYtOTc0YTllZDdiY2ZlLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA0MDglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNDA4VDIzMjkzN1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWM5MDM5Y2U2OWQ5NTU3ZDAyNjk3NTM1YmIyMjllYzc0ZmEyOTVhNGVlMzJjZDE4OTc1MzY2ODIwMGFkYjdlODUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.D5BSg4VnXV157ldq8YT9eHrvAbhgTFDj_daCst4537E)

Can you share an MRP for it?

> Also, is it possible to do the baking on a thread, not to freeze the UI?

All shader baking work does happen in separate threads already so I think it's just a matter of figuring out how to make the thread that's waiting for the workers to do UI updates.

--- ghuser404:
@DarioSamo 
[shader-baker.zip](https://github.com/user-attachments/files/19658484/shader-baker.zip)


--- DarioSamo:
@ghuser404 This should be fixed now, turns out D3D12's shader baker was using a shader model that was too low for FSR2's FP16 variants to build correctly.

--- DarioSamo:
> Also, is it possible to do the baking on a thread, not to freeze the UI?

This should also be fixed! There's a new editor progress now that refreshes on every baked shader.

--- DarioSamo:
The PR is mostly complete except for the one point I listed out in the TODO, we're good to start reviewing it.

--- DarioSamo:
> I get a warning when exporting a project with shader baking enabled (the project is using Forward+ and the default drivers):
> 
> ```
>   WARNING: core/config/project_settings.cpp:405 - Property not found: 'rendering/rendering_device/driver.linux'.
> ```

Seems like querying for a setting that doesn't exist results in that. Is there some way to do so without triggering the warning? It's just for checking whether the OS in particular has an override for the driver setting.


--- DarioSamo:
> The Shader Baker > Export option should be renamed to Shader Baker > Enabled option, for consistency with other boolean options in export presets.

This is done now.

--- Calinou:
> Seems like querying for a setting that doesn't exist results in that. Is there some way to do so without triggering the warning? It's just for checking whether the OS in particular has an override for the driver setting.

I'm not sure if this exists. This would probably warrant new methods with a `_or_null()` suffix that quietly fail and return `null` if the project setting doesn't exist. 

I've opened a PR for this: https://github.com/godotengine/godot/pull/105951

--- vbettaque:
Not really related to the shader baking itself, but I really appreciate you refactoring the SPIR-V reflection routines and making them device-independent. I'm currently working on a PR to expose shader reflection bindings to the user, and this will come in really handy once it's merged (hopefully soon) :)

--- DarioSamo:
Rebased on top of latest master along with the suggestions.

--- TCROC:
Is this PR ready to be tested?

--- DarioSamo:
> Is this PR ready to be tested?

Yes

--- TCROC:
Also quick question, can D3D12 be compiled from linux devices?  I see the potential for it was mentioned here: https://github.com/godotengine/godot/pull/102552#issuecomment-2648153706.  Just curious if that is being included in this pr :)

--- DarioSamo:
> Just curious if that is being included in this pr :)

It's not, I consider it beyond the scope of the PR at the moment but it's certainly doable.

--- TCROC:
Thank you for the update!  I left some reviews on some issues I encountered along with the suggested fixes.

I believe headless builds are intended to work with this PR though right?  Based on the comments I was reading.  Specifically this one here:

https://github.com/godotengine/godot/pull/102552#issuecomment-2648153706

> The shader classes aren't tied to a particular driver running. No GPU is required for the process, as that was part of most of the refactoring that was done to take it out of the drivers and into their own classes that can be used independently.

I believe the crash should be reproducible with the MPR in the issue here: https://github.com/godotengine/godot/issues/94734

--- TCROC:
running my tests, vulkan baking doesn't appear to be cross platform compatible.  Is this expected?  Or at least, cross OS compatible.  It seems that vulkan shaders from my POP OS device are missed on my android device.  Even though I compile both with Mobile rendering

--- DarioSamo:
> running my tests, vulkan baking doesn't appear to be cross platform compatible. Is this expected? Or at least, cross OS compatible. It seems that vulkan shaders from my POP OS device are missed on my android device. Even though I compile both with Mobile rendering

They should be compatible, but I can't think of what could cause them to differ. Are they all entirely missed? You'll probably need to gather some information about it somehow, either if the base hash matches or something else is missing.

--- TCROC:
> They should be compatible, but I can't think of what could cause them to differ. Are they all entirely missed? You'll probably need to gather some information about it somehow, either if the base hash matches or something else is missing.

I'm gathering that info as we speak :)  

I can confirm that it is the first part of the has that is a mismatch:

```
.godot/shader_cache/SceneForwardMobileShaderRD/6be8654b8db7aec35e34af908aafd0a2448b03d0ad33f26f44fb8a9015743f56/d117d0d3628009598ca01da3412c79ed73cc3498
```

specifically this part:

```
6be8654b8db7aec35e34af908aafd0a2448b03d0ad33f26f44fb8a9015743f56
```

Which is why I've added a ``print_line`` to initialize cache to see how the 2 platforms generate their hashes:

```cpp
void ShaderRD::_initialize_cache() {
	shader_cache_user_dir_valid = !shader_cache_user_dir.is_empty();
	if (!shader_cache_user_dir_valid) {
		return;
	}

	for (const KeyValue<int, LocalVector<int>> &E : group_to_variant_map) {
		StringBuilder hash_build;

		hash_build.append("[base_hash]");
		hash_build.append(base_sha256);
		hash_build.append("[general_defines]");
		hash_build.append(general_defines.get_data());
		hash_build.append("[group_id]");
		hash_build.append(itos(E.key));
		for (uint32_t i = 0; i < E.value.size(); i++) {
			hash_build.append("[variant_defines:" + itos(E.value[i]) + "]");
			hash_build.append(variant_defines[E.value[i]].text.get_data());
		}

		print_line("string " + hash_build.as_string() + " text " + hash_build.as_string().sha256_text());
```

Build just finished.  Going to grab those details.

--- DarioSamo:
Cool, dumping `tohash` from ShaderRD along with the other bits you can find should give a pretty good indication of what's different.

--- TCROC:
> Cool, dumping tohash from ShaderRD along with the other bits you can find should give a pretty good indication of what's different.

And they have!  There does appear to be something screwy going on.  Looks like the android shaders are indeed different:

[android_shaders.log](https://github.com/user-attachments/files/20354288/android_shaders.log)
[desktop_shaders.log](https://github.com/user-attachments/files/20354289/desktop_shaders.log)

Attached are the 2 logs after I cleaned them up.  Its looks like we are running into issues with ``ParticlesShaderRD (group 0)``, ``SceneForwardMobileShaderRD (group 0)``, and ``SceneForwardMobileShaderRD (group 1)``.

Here's them being compared with a diff tool in vs code:

The first one in ParticleShaderRD with desktop compared to android:

## ParticleShaderRD

![image](https://github.com/user-attachments/assets/c4b9cbc6-b76b-44bd-a82b-e583847d4aa4)

For whatever reason, this one just doesn't load all the way on android.  I reran it multiple times to confirm.

Next are the ``SceneForwardMobileShaderRD``'s

## SceneForwardMobileShaderRD (group 0)

![image](https://github.com/user-attachments/assets/9977a968-8110-4063-aed1-170e0d0ec1bf)

## SceneForwardMobileShaderRD (group 1)

![image](https://github.com/user-attachments/assets/016c232c-26eb-4e30-a296-25f0b7c6e924)

It looks like the ``USE_RADIANCE_CUBEMAP_ARRAY`` gets flip flopped between the two shaders.  It is present in ``(group 0)`` on desktop and not in ``(group 1)`` on desktop.  And vice versa on Android.  Which is throwing the hashes off.

Note:

There could be an issue with the logging on Android in regards to the particles.  I'd be curious to see what happens when we resolve this ``USE_RADIANCE_CUBEMAP_ARRAY`` flip flop before we figure out why ParticleShader is cut off on Android.  That could be as simple as being too long for the stdout or something silly

--- DarioSamo:
As far as I can tell, USE_RADIANCE_CUBEMAP_ARRAY is defaulted to true on project settings but false on mobile. Therefore, the shader baker can't see it on the host system because the project setting is different on each platform and it causes the base shader to be different instead of being a variant.

I'll think about what can be done but that explains it.

--- TCROC:
I'll manually set it to false in my project settings real quick to see what happens.

--- TCROC:
What is the project setting name?

--- TCROC:
Found it! :)

![image](https://github.com/user-attachments/assets/84d9dd0b-b012-4e1c-8414-6683deb252b6)


--- TCROC:
Okay so we made progress.  The hashes are now matching, but I'm still getting misses on android.  Example:

```
05-20 16:33:23.955 27556 27591 I godot   : Shader cache miss for SceneForwardMobileShaderRD/6be8654b8db7aec35e34af908aafd0a2448b03d0ad33f26f44fb8a9015743f56/7ec768f7b21c0731c7c1c7697c1add01926da9a7
```

Even though its clearly there when extracting the apk:

```
tcroc@pop-os:~/dev/BlockyBallOT/blockyball-godot-target/android/apk/release/blockyballot/assets/.godot/shader_cache/SceneForwardMobileShaderRD/6be8654b8db7aec35e34af908aafd0a2448b03d0ad33f26f44fb8a9015743f56$ ls | grep 7ec768f7b21c0731c7c1c7697
7ec768f7b21c0731c7c1c7697c1add01926da9a7.vulkan.cache
```

--- TCROC:
Found the issue. The ``Ref<DirAccess>`` is unable to ``change_dir`` into the "shader_cache" even though that directory is clearly there:

![image](https://github.com/user-attachments/assets/a2b728be-e5ab-4e4e-bfa8-767f6522af46)

And here is the unpacked apk showing it exists:

![image](https://github.com/user-attachments/assets/8437ca3a-c9d9-4c2f-bd7b-3b48f01805f6)

My guess is that you can't call ``change_dir`` in the ``res://`` on Android.  Idk, but its just a guess.  I'm going to attempt just opening up the directory with the full path and see what happens

--- TCROC:
Yep.  That does indeed seem to be the case.  Doing it like so works on android:

![image](https://github.com/user-attachments/assets/3b775cc2-a9cc-4911-9ce9-b6819d66b635)

But now we run into a new issue...

When we get to this part of the execution:

![image](https://github.com/user-attachments/assets/68a4447c-a540-4501-89ea-0d30a9abd16d)

shader_cache_res_dir and shader_cache_user_dir are both null...

![image](https://github.com/user-attachments/assets/3a6f735c-8637-4d36-b306-77076ef0f1e8)

![image](https://github.com/user-attachments/assets/90b08230-2189-48f4-94e2-1f9b608d7222)

Is there some kind of auto memory management going on that is freeing these strings?  Potential bug with the ``String`` class itself?

--- TCROC:
Those things listed above definitely improve on it a lot and result in more cache hits.  There's still a surprising amount of misses on Android.  We will have to continue debugging as to why.

Also, GPU particles always cache miss.  Even if running on the same desktop it was exported from and to.

--- DarioSamo:
How to solve USE_RADIANCE_CUBEMAP_ARRAY still evades me a bit as it's a bit of a peculiar case.

- We have a very limited amount of default overrides specific to _mobile_ platforms (but _not_ the mobile renderer).
- `"rendering/reflections/sky_reflections/texture_array_reflections"` is the setting in question.
- Whether this is true or not will indicate whether an entire `#define` that controls code inside the shader makes it through.
- USE_RADIANCE_CUBEMAP_ARRAY controls whether textureCubeArray or textureCube is used, so turning it into a spec constant isn't possible unless we decide on only one type of input.
- We're lacking a lot of infrastructure at the moment for being able to effectively decouple how shaders are created _separated_ from the current renderer that is chosen.

It might be easier to fix this in a future refactor, but we might just need to chalk this down to a bit of documentation or possibly an export warning until it is fixed to make sure these settings both match for the shader baking to work as intended.

--- TCROC:
> How to solve USE_RADIANCE_CUBEMAP_ARRAY still evades me a bit as it's a bit of a peculiar case.
> 
>     * We have a very limited amount of default overrides specific to _mobile_ platforms (but _not_ the mobile renderer).
> 
>     * `"rendering/reflections/sky_reflections/texture_array_reflections"` is the setting in question.
> 
>     * Whether this is true or not will indicate whether an entire `#define` that controls code inside the shader makes it through.
> 
>     * USE_RADIANCE_CUBEMAP_ARRAY controls whether textureCubeArray or textureCube is used, so turning it into a spec constant isn't possible unless we decide on only one type of input.
> 
>     * We're lacking a lot of infrastructure at the moment for being able to effectively decouple how shaders are created _separated_ from the current renderer that is chosen.
> 
> 
> It might be easier to fix this in a future refactor, but we might just need to chalk this down to a bit of documentation or possibly an export warning until it is fixed to make sure these settings both match for the shader baking to work as intended.

Its actually even more than just a ``USE_RADIANCE_CUBEMAP_ARRAY`` issue.  I left a comment here:

https://github.com/godotengine/godot/pull/102552#pullrequestreview-2856005724

Rather I think the solution is probably to add a feature that instructs the godot editor to load ``project.godot`` under specific subsettings.

Example:

If you want godot editor to run with ``.mobile`` settings such as ``rendering/reflections/sky_reflections/texture_array_reflections.mobile``, you would run a command such as:

```
godot --export-release android-preset --config-mode mobile
```

 And even better, when running with the ``--export-release`` or ``--export-debug`` flag, it would automatically load the proper ``--config-mode`` for the device / platform. Unless the ``config-mode`` was manually supplied.
 
 But yes, this may be better suited for a separate PR.  For my particular case, I can just have our pipeline hot swap out the ``project.godot`` with one configured for the default mobile settings.
 
Its not intuitive and requires the end user to have knowledge of godot's default device / platform settings.  In my case, I had to dig through the source code.  But its a fine workaround for me for now.  Other users may be confused as to why their shaders aren't baking on mobile platforms.

--- akien-mga:
For the issue of using `.mobile` overloads to apply the target's setting for shader compilation, I believe this should be possible since https://github.com/godotengine/godot/pull/71542 (merged for 4.5). CC @bruvzg

--- bruvzg:
> I believe this should be possible since https://github.com/godotengine/godot/pull/71542 (merged for 4.5)

It's specifically for getting project settings with target overrides (use `get_project_setting(p_preset, "setting")` with export preset instead of `GLOBAL_GET("setting")`), not sure if it's sufficient for shader compiler.

--- TCROC:
lol.  I think something went wrong in one of the last few commits 😅

![image](https://github.com/user-attachments/assets/e1a3b278-def2-4c9a-8844-8f553ba9b0a1)


--- TCROC:
fortunately I created a backup of a working branch: https://github.com/Lange-Studios/godot/tree/shader-baker-ls-backup

Hopefully that helps to reference :)

Edit:

Here's @DarioSamo 's working commit without the noise of the extra commits in my branch: https://github.com/lange-studios/godot/commit/5a00cb85ed8640acac572d1cb08b1de10db306b7

--- TCROC:
And another thing on latest tests:

Headless exports no longer crash, but the shader baker also no longer runs in headless mode.  Like just doesn't run at all.  So headless exports are still not working.

--- DarioSamo:
> For the issue of using `.mobile` overloads to apply the target's setting for shader compilation, I believe this should be possible since #71542 (merged for 4.5). CC @bruvzg

Sadly it's not quite enough, because the issue lies deeper at an architectural level.

The origin of the issue is the same cause as why we can't export to a different platform with the shader baker enabled while on a different renderer than what the target platform will use. We only have one global instance of the renderer initialized, and all material storage goes to it to reference and know what shader data it must create. This setting in particular adds one `#define` during initialization of the renderer during program startup.

We need an architectural change to completely decouple shader libraries from renderers to be able to instance the set of shaders a renderer will use _separately_ from the one currently in use. We consider this to be mostly out of scope of the current PR because it's an effort that'd take quite a bit of time and it's mostly an incremental improvement at the end of the day on a quirk that isn't too hard to work around for now.

My current proposal is we just appropriately warn on the export for these particular settings. There's only two of them at the moment, this one and the barley diffuse one, so we can tell users who export to mobile platforms to make sure these settings are consistent on their project as well on desktop before doing it for now.

The shader library system I'm talking about is mostly just a concept for the time being so it's hard to say how long it'd take to do, but it's basically the point that'll completely solve the problem of us needing to be on the right renderer with the right settings to export to a particular platform.

--- DarioSamo:
> Headless exports no longer crash, but the shader baker also no longer runs in headless mode. Like just doesn't run at all. So headless exports are still not working.

Shader Baker won't be able to run in headless mode if no Renderer is present due to the reasons I mentioned above just yet.

--- TCROC:
> > Headless exports no longer crash, but the shader baker also no longer runs in headless mode. Like just doesn't run at all. So headless exports are still not working.
> 
> Shader Baker won't be able to run in headless mode if no Renderer is present due to the reasons I mentioned above just yet.

Ah... it can't run in headless mode for the same reason as the ``.mobile`` configs and such?  The reasons listed here? https://github.com/godotengine/godot/pull/102552#issuecomment-2901074390

--- DarioSamo:
> fortunately I created a backup of a working branch: https://github.com/Lange-Studios/godot/tree/shader-baker-ls-backup
> 
> Hopefully that helps to reference :)
> 
> Edit:
> 
> Here's @DarioSamo 's working commit without the noise of the extra commits in my branch: [Lange-Studios@5a00cb8](https://github.com/Lange-Studios/godot/commit/5a00cb85ed8640acac572d1cb08b1de10db306b7)

I don't recall any changes that could cause issues, but there's no mention of the platform or the renderer in use so I'd need that to narrow anything down first.

--- DarioSamo:
> Ah... it can't run in headless mode for the same reason as the `.mobile` configs and such? The reasons listed here? [#102552 (comment)](https://github.com/godotengine/godot/pull/102552#issuecomment-2901074390)

Yeah, without a renderer being instanced we have no way of pulling the shaders available yet. That's a deeper architectural change that will have to happen in a future PR, but it'd be a really extensive PR as well, probably as big as this one.

--- TCROC:
> > fortunately I created a backup of a working branch: https://github.com/Lange-Studios/godot/tree/shader-baker-ls-backup
> > Hopefully that helps to reference :)
> > Edit:
> > Here's @DarioSamo 's working commit without the noise of the extra commits in my branch: [Lange-Studios@5a00cb8](https://github.com/Lange-Studios/godot/commit/5a00cb85ed8640acac572d1cb08b1de10db306b7)
> 
> I don't recall any changes that could cause issues, but there's no mention of the platform or the renderer in use so I'd need that to narrow anything down first.

I'll go test your latest force push and see if I can recreate it + give you those additional details.

--- TCROC:
> > Ah... it can't run in headless mode for the same reason as the `.mobile` configs and such? The reasons listed here? [#102552 (comment)](https://github.com/godotengine/godot/pull/102552#issuecomment-2901074390)
> 
> Yeah, without a renderer being instanced we have no way of pulling the shaders available yet. That's a deeper architectural change that will have to happen in a future PR, but it'd be a really extensive PR as well, probably as big as this one.

Should we removed the attached issue fix then? https://github.com/godotengine/godot/issues/94734

Since it still won't be able to import glsl shaders in headless mode?

--- TCROC:
Oh wait... or does this allow them to be imported and exported?  Just not baked?

--- DarioSamo:
> Oh wait... or does this allow them to be imported and exported? Just not baked?

That's it. This PR happens to fix the fact it is no longer coupled to the renderer to be able to compile a shader. Baking them is a very different story and I don't think there's any mechanism to bake it yet.

--- DarioSamo:
For the record, it's not really a requirement for this PR to hit a 100% rate on all possible types of shader caches we have available, and there's future improvements planned still. We have a lot of interest for this to be as good as possible, but it also makes it significantly harder to maintain the longer the feature is not part of the engine due to the amount of changes it introduces.

As it stands, if the PR can give a benefit to the current workflow, which is basically no shader caches at all, then it's already a pretty significant improvement.

--- TCROC:
> For the record, it's not really a requirement for this PR to hit a 100% rate on all possible types of shader caches we have available, and there's future improvements planned still. We have a lot of interest for this to be as good as possible, but it also makes it significantly harder to maintain the longer the feature is not part of the engine due to the amount of changes it introduces.
> 
> 
> 
> As it stands, if the PR can give a benefit to the current workflow, which is basically no shader caches at all, then it's already a pretty significant improvement.

Makes sense. My tests seem to indicate we are sitting at close to 100% with vulkan (if not 100%). And 100% on iOS metal. The shader is just erroring out on being null on metal.

Point being tho, I think we might be at 100% already. If not we are really close. Load times DRASTICALLY improve.

So I guess question would be, should we hold the PR up to get metal working here? https://github.com/godotengine/godot/pull/102552#pullrequestreview-2861644965

Or should we push through and open a separate issue? I'm fine with either.

--- TCROC:
> > fortunately I created a backup of a working branch: https://github.com/Lange-Studios/godot/tree/shader-baker-ls-backup
> > Hopefully that helps to reference :)
> > Edit:
> > Here's @DarioSamo 's working commit without the noise of the extra commits in my branch: [Lange-Studios@5a00cb8](https://github.com/Lange-Studios/godot/commit/5a00cb85ed8640acac572d1cb08b1de10db306b7)
> 
> I don't recall any changes that could cause issues, but there's no mention of the platform or the renderer in use so I'd need that to narrow anything down first.

Issue is still occurring:

![image](https://github.com/user-attachments/assets/692537ec-4c2d-4ea7-a5f2-56047792e522)

Here's the log: [game.log](https://github.com/user-attachments/files/20399152/game.log)

Vulkan / Forward+ / Linux / Double Precision / Dotnet

--- TCROC:
Okay!  I think all issues that would have been blocking this PR are almost resolved!  We only have 2 remaining:

1. https://github.com/godotengine/godot/pull/102552#issuecomment-2902303364
2. https://github.com/godotengine/godot/pull/102552#discussion_r2098995038

I agree with @DarioSamo that something doesn't feel right about issue 2.  But I can confirm via my debugger that this is how it behaves on Android.  At least on my Android device.  This may be a separate issue that needs opening regarding the behavior of ``String`` though.  I don't think it needs to hold up this PR.

Thank you so much for all the hard work put in to this PR!  The load time improvements are huge!  I hope my feedback has been equally helpful.

I'll put in a follow up issue regarding the pain points I've run into and how this can be improved.  But all in all, I think we are just about at the finish line with this!

--- TCROC:
For issue: https://github.com/godotengine/godot/pull/102552#issuecomment-2902303364

Here's an MRP: [mrp-broken-shader-baker.zip](https://github.com/user-attachments/files/20403593/mrp-broken-shader-baker.zip)

## Broken (this branch) ❌

![image](https://github.com/user-attachments/assets/e4a3c3cf-e7cd-4c5b-87fa-4ad14d6cb364)

## Good ✅ (used with last working build)

![image](https://github.com/user-attachments/assets/4f84748c-1dc5-4f92-bf8e-14c782b3301b)

NOTE: I also tested this in our fork after syncing with godot master and not the shader baker. I had to delete the .godot folder and reimport.  After doing so, things worked again.  The issue seems to reside within the .godot folder becoming corrupted.

## Details

Vulkan / Forward+ / Pop OS (Linux / Ubuntu) / Double Precision / Dotnet

--- DarioSamo:
@TCROC It seems the texture import itself is broken. It seems the ShaderRDFile is not receiving the MODULE_GLSLANG_ENABLED macro as it should. I'll look into it.

--- DarioSamo:
Thanks for the report, it seemed the key was indeed deleting the .godot folder to trigger a reimport. Should be fixed now, but you might need to delete it again so it reimports it.

--- TCROC:
> Thanks for the report, it seemed the key was indeed deleting the .godot folder to trigger a reimport. Should be fixed now, but you might need to delete it again so it reimports it.

You are very welcome!  I've been testing platforms and so far things are going good!  Only 1 cache miss on Linux Forward+:

```
Shader cache miss for IntegrateDfgShaderRD/3d558a6bcc6d1369fa9ce043aa28fe80c3cadb908d3425840ae12eea0680c4ec/087916079fba7c625e62b0c2cca570e0fb87c99a
```

Which like you said, 100% cache hits aren't needed for this PR.  And this was only on startup.  The expensive shaders were all cache hits.  Testing Android now and then gonna test iOS.  All in all, looking good and your change fixed https://github.com/godotengine/godot/pull/102552#issuecomment-2903166573

--- TCROC:
AYO!!  All is working as expected!!  The two remaining issues can me marked resolved!

1. https://github.com/godotengine/godot/pull/102552#issuecomment-2902303364 ✅
2. https://github.com/godotengine/godot/pull/102552#discussion_r2098995038 ✅

Lets get this PR pushed through! :)

--- TCROC:
Great work @DarioSamo @kisg @stuartcarnie @RandomShaper and everyone else involved in this PR that I may be leaving out.  This improves load times tremendously!  Very well done!

--- TCROC:
Is there anything else needed to push this pr through?

--- DarioSamo:
> ```
> Shader cache miss for IntegrateDfgShaderRD/3d558a6bcc6d1369fa9ce043aa28fe80c3cadb908d3425840ae12eea0680c4ec/087916079fba7c625e62b0c2cca570e0fb87c99a
> ```

This one should be fixed now.

--- TCROC:
> > ```
> 
> > Shader cache miss for IntegrateDfgShaderRD/3d558a6bcc6d1369fa9ce043aa28fe80c3cadb908d3425840ae12eea0680c4ec/087916079fba7c625e62b0c2cca570e0fb87c99a
> 
> > ```
> 
> 
> 
> This one should be fixed now.

Brilliant! I'll test it out!

--- TCROC:
@DarioSamo 2 updates below

1. Shader Cache Miss ✅
2. Vulkan Validation Layers ❌

### 1. Shader Cache Miss

> > ```
> > Shader cache miss for IntegrateDfgShaderRD/3d558a6bcc6d1369fa9ce043aa28fe80c3cadb908d3425840ae12eea0680c4ec/087916079fba7c625e62b0c2cca570e0fb87c99a
> > ```
> 
> This one should be fixed now.

I can confirm that it is fixed for Linux and Android.  I suspect it applies to the other platforms as well.  I'll keep an eye out as I test them.

### 2 Vulkan Validation Layers

Running on my Galaxy S10e with ``Vulkan Validation Layers``, I get a bunch of errors related to the baked shaders being compiled with SPIRV version 1_5 when my device only supports up to version 1_3.  Digging further I see that 71% of devices are using ``Vulkan 1.1``: https://developer.android.com/about/dashboards/#Vulkan

And then digging further:

https://stackoverflow.com/a/63497848
https://github.com/google/shaderc/tree/main/glslc#426---target-env

> Generated code uses SPIR-V 1.0, except for code compiled for Vulkan 1.1, which uses SPIR-V 1.3, and code compiled for Vulkan 1.2, which uses SPIR-V 1.5.

So I went and changed 

drivers/vulkan/rendering_shader_container_vulkan.cpp
```cpp
RenderingDeviceCommons::ShaderSpirvVersion RenderingShaderContainerFormatVulkan::get_shader_spirv_version() const {
	return SHADER_SPIRV_VERSION_1_5;
}
```

To:

```cpp
RenderingDeviceCommons::ShaderSpirvVersion RenderingShaderContainerFormatVulkan::get_shader_spirv_version() const {
	return SHADER_SPIRV_VERSION_1_3;
}
```

And the validation errors went away! :)

And do to the method above:

```cpp
RenderingDeviceCommons::ShaderLanguageVersion RenderingShaderContainerFormatVulkan::get_shader_language_version() const {
	return SHADER_LANGUAGE_VULKAN_VERSION_1_1;
}
```

It should indeed be using ``SHADER_SPIRV_VERSION_1_3`` instead of ``SHADER_SPIRV_VERSION_1_5``.

But this does lead to a more nuanced question:

Should we allow users to customize which version they want to support via settings?  That doesn't necessarily have to be done in this PR either.  We can do that in a different PR.  The only thing we should be fixing in this PR is changing ``SHADER_SPIRV_VERSION_1_5`` -> ``SHADER_SPIRV_VERSION_1_3`` in order to be compatible with the Vulkan specifications.

--- DarioSamo:
> We need to change SHADER_SPIRV_VERSION_1_5 to SHADER_SPIRV_VERSION_1_3 in order to be compatible with the Vulkan version 1.1 we are targetting. Details here: [#102552 (comment)](https://github.com/godotengine/godot/pull/102552#issuecomment-2912789702)

As far as I know, the version in use was whatever the host device supported.

Under most engines I've seen, the shader version is picked by the build system to target the lowest common denominator they wish to target. It makes sense to reduce the version.

--- AThousandShips:
You can use the batch option to add multiple suggestions!

--- DarioSamo:
> You can use the batch option to add multiple suggestions!

I just realized that as you typed it, sorry!

--- clayjohn:
> Should we allow users to customize which version they want to support via settings? That doesn't necessarily have to be done in this PR either. We can do that in a different PR. The only thing we should be fixing in this PR is changing `SHADER_SPIRV_VERSION_1_5` -> `SHADER_SPIRV_VERSION_1_3` in order to be compatible with the Vulkan specifications.

@TCROC No, we should just target the lowest version that we actually require. If everything works with version 1.3, then we should just fix the target at 1.3, there is no benefit to targetting a higher version than needed

--- TCROC:
> > Should we allow users to customize which version they want to support via settings? That doesn't necessarily have to be done in this PR either. We can do that in a different PR. The only thing we should be fixing in this PR is changing `SHADER_SPIRV_VERSION_1_5` -> `SHADER_SPIRV_VERSION_1_3` in order to be compatible with the Vulkan specifications.
> 
> @TCROC No, we should just target the lowest version that we actually require. If everything works with version 1.3, then we should just fix the target at 1.3, there is no benefit to targetting a higher version than needed

The setting would be for allowing users to select both their vulkan and spirv versions.  I was reading online and it sounds like certain devices require different versions.  But this is out of scope of this PR.  For now changing to ``SHADER_SPIRV_VERSION_1_3`` will suffice.

--- DarioSamo:
> The setting would be for allowing users to select both their vulkan and spirv versions. I was reading online and it sounds like certain devices require different versions. But this is out of scope of this PR. For now changing to `SHADER_SPIRV_VERSION_1_3` will suffice.

What largely controls the shader version is what shader features you wish to use, so you don't really get much use out of being able to control this unless you have something else that goes along with it that lets you disable certain features that have a minimum version requirement.

--- TCROC:
> > The setting would be for allowing users to select both their vulkan and spirv versions. I was reading online and it sounds like certain devices require different versions. But this is out of scope of this PR. For now changing to `SHADER_SPIRV_VERSION_1_3` will suffice.
> 
> What largely controls the shader version is what shader features you wish to use, so you don't really get much use out of being able to control this unless you have something else that goes along with it that lets you disable certain features that have a minimum version requirement.

Gotcha... so should we change to ``SPIRV 1.3`` instead of ``SPIRV 1.5`` since we are targetting ``Vulkan 1.1``?  And from what I've been reading, the max ``SPIRV`` for ``Vulkan 1.1`` is ``SPIRV 1.3``.  Vulkan validation gets spammed with errors on my Samsung Galaxy S10e saying to downgrade.

https://github.com/godotengine/godot/pull/102552#pullrequestreview-2871407623

--- DarioSamo:
> Gotcha... so should we change to `SPIRV 1.3` instead of `SPIRV 1.5` since we are targetting `Vulkan 1.1`?

I already applied the change on the PR. If something shows up that has a higher version requirement we'll need to figure out a mechanism for shaders to specify they need it and be excluded from baking if the version is too low.

--- TCROC:
> > Gotcha... so should we change to `SPIRV 1.3` instead of `SPIRV 1.5` since we are targetting `Vulkan 1.1`?
> 
> I already applied the change on the PR. If something shows up that has a higher version requirement we'll need to figure out a mechanism for shaders to specify they need it and be excluded from baking if the version is too low.

Sounds like a plan!  I have a list of features / pain points that I'll put an issue in to track once this PR goes through.

Thanks @DarioSamo ! :)

--- stuartcarnie:
> Also, just to confirm, we are officially dropping MoltenVK support for the Forward+ renderer with this change right?

Is there a reason to drop MoltenVK? Doing so would eliminate support for x86_64 hardware – my understanding is shader baking will still work with MoltenVK.

--- TCROC:
I would prefer to keep x86_64 support if we can. We intend to support x86_64 macs with our next release.

--- DarioSamo:
> Is there a reason to drop MoltenVK?

The subgroups macro duplicates the amount of variants we'd need in critical shaders like the Forward+ material, which leads to a a combinatory explosion. They're also just not very well maintained in general and I don't think anybody's actively checking if they work properly or not. It adds a lot of complexity to our shader code to maintain these paths, so when I was tasked with this I was told to remove them.

I can't really support doubling up shader baking times and materials entirely just to support that subset of hardware so I don't think having them as a real variant is a solution.

The only compromise we could take is not baking the subgroup-less paths, so these systems just hit cache misses but compile them on the client as always, but I feel it won't address the problem of having to carry code that is not actively being maintained and may break in further refactors.

--- TCROC:
> but I feel it won't address the problem of having to carry code that is not actively being maintained and may break in further refactors.

So will this PR remove support for x86_64 macbooks?  Not just shader baking, but in general?

--- DarioSamo:
For the sake of completeness, the affected shaders by the subgroups macro are:
- scene_forward_clustered.glsl
- cluster_render.glsl
- taa_resolve.glsl
- volumetric_fog_process.glsl (this one we actually preferred *not* to use subgroups so it goes away entirely for both cases)

--- DarioSamo:
> So will this PR remove support for x86_64 macbooks? Not just shader baking, but in general?

It explicitly "breaks" the three shaders I mentioned above if it so happens that the current situation with MoltenVK remains the same and for whatever reason Metal doesn't work on them. This is not a case of explicit support but workarounds for bugs being removed.

For example, I'm not aware if the current Metal backend works fine on these devices either when it comes to these effects.

--- TCROC:
> > So will this PR remove support for x86_64 macbooks? Not just shader baking, but in general?
> 
> It explicitly "breaks" the four shaders I mentioned above if it so happens that the current situation with MoltenVK remains the same and for whatever reason Metal doesn't work on them. This is not a case of explicit support but workarounds for bugs being removed.
> 
> For example, I'm not aware if the current Metal backend works fine on these devices either when it comes to these effects.

Ah I see.  So will ``forward_mobile`` and / or ``compatibility`` still work with x86_64?

--- DarioSamo:
> Ah I see. So will forward_mobile and / or compatibility still work with x86_64?

It should, although the TAA shader is also available on mobile but not really enforced by default or even desired usually, as MSAA is much more preferable on these devices. If the errors I mentioned due to lack of proper subgroup support still exist, you can very much work around it by just using `mobile`.

Compatibility is not affected at all by this PR.

--- bruvzg:
> and for whatever reason Metal doesn't work on them.

Current Metal is implemented for Apple Silicon only, Intel Macs only use MoltenVK.

--- TCROC:
> It should, although the TAA shader is also available on mobile but not really enforced by default or even desired usually, as MSAA is much more preferable on these devices. If the errors I mentioned due to lack of proper subgroup support still exist, you can very much work around it by just using mobile.
> Compatibility is not affected at all by this PR.

Perfect!  I'm fine with this :)

> Current Metal is implemented for Apple Silicon only, Intel Macs only use MoltenVK.

@DarioSamo You **didn't** removed MoltenVK support right?  Just those shaders you listed?  So MoltenVK _should_ still work with ``mobile`` and ``compatibility`` renderers via MoltenVK?

--- DarioSamo:
> Current Metal is implemented for Apple Silicon only, Intel Macs only use MoltenVK.

Yeah I can see we have a explicit path to go back to Vulkan under those cases.

```cpp
#if defined(__x86_64__)
	bool fallback_to_vulkan = GLOBAL_GET("rendering/rendering_device/fallback_to_vulkan");
	if (!fallback_to_vulkan) {
		WARN_PRINT("Metal is not supported on Intel Macs, switching to Vulkan.");
	}
	// Metal rendering driver not available on Intel.
	if (rendering_driver == "metal") {
		rendering_driver = "vulkan";
		OS::get_singleton()->set_current_rendering_driver_name(rendering_driver);
	}
#endif
```

So it seems we fall under this case regardless, as the Metal driver on Godot's side is the one that lacks support for these devices.

A possibility remains that the situation may have changed under newer versions of MoltenVK, but I lack the devices to verify this.

> You didn't removed MoltenVK support right? Just those shaders you listed? So MoltenVK should still work with mobile and compatibility renderers via MoltenVK?

You don't explicitly support MoltenVK, there just happens to be specific workarounds on those shaders. Presumably it'll still run and either show visual errors (when using the shaders I mentioned) or not if it's been somehow fixed since the moment the workaround was added.

--- bruvzg:
> So MoltenVK should still work with mobile and compatibility renderers via MoltenVK?

Compatibility is native OpenGL, MoltenVK is not required.

--- TCROC:
> You don't explicitly support MoltenVK, there just happens to be specific workarounds on those shaders. Presumably it'll still run and either show visual errors (when using the shaders I mentioned) or not if it's been somehow fixed since the moment the workaround was added.

Ah I see.

> A possibility remains that the situation may have changed under newer versions of MoltenVK, but I lack the devices to verify this.

I have the devices.  I will test! :)

> Compatibility is native OpenGL, MoltenVK is not required.

Perfect!  As long as there is a way to support the devices, I'm fine with that :).  They are older devices as this point, so a visually degraded experience is to be expected.

--- DarioSamo:
>  They are older devices as this point, so a visually degraded experience is to be expected.

I believe this is pretty much the conclusion we reached last time. Pretty much all affected shaders are Forward+, which is probably too heavy of a renderer to run on these older systems anyway, and they certainly won't be using TAA either. You can very much block access to these options in these devices _if_ they happen to break.

--- Calinou:
> It should, although the TAA shader is also available on mobile but not really enforced by default or even desired usually, as MSAA is much more preferable on these devices. If the errors I mentioned due to lack of proper subgroup support still exist, you can very much work around it by just using mobile.

The mobile renderer doesn't have motion vectors yet, and even with https://github.com/godotengine/godot/pull/100283, the motion vectors available aren't precise enough for TAA to work. Not to mention TAA is currently quite expensive due to motion vector generation, so I doubt it would be viable on mobile without a rewrite.

--- clayjohn:
A note for the release notes:

This is an optional feature that can be enabled at export time to speed up shader compilation massively. However, it comes with tradeoffs:
1. Export time will be much longer
2. Build size will be much larger since the baked shaders can take up a lot of space
3. We have removed several MoltenVK bug workarounds from the Forward+ shader, therefore we no longer guarantee support for the Forward+ renderer on intel Macs. If you are targeting intel Macs, you should use the Mobile or Compatibility renderers

Baking for Vulkan can be done from any device, but baking for D3D12 needs to be done from a Windows device (@DarioSamo please confirm) and baking for Apple devices need to be from an Apple device (@stuartcarnie please confirm).

This feature works with ubershaders automatically without any work from the user. Using shader baking is strongly recommended when targeting Apple devices or D3D12 since it makes the biggest difference there (over 20x decrease in load times in the TPS demo)

--- TCROC:
> This is an optional feature that can be enabled at export time to speed up shader compilation massively

This brings about a question from me.  What other features does Godot have (if any) for frontloading things of high computation at export time?  If others, a page in the godot book regarding improving load times and performance (if one doesn't exist already) would be really useful

--- stuartcarnie:
@clayjohn 

> and baking for Apple devices need to be from an Apple device

There are two levels of baking for Apple platforms

1. SPIR-V → Metal Shader Language (MSL) always works, and is available on any host OS
2. MSL → `.metallib` is where the Metal compiler exists (macOS with Xcode / Command Line Tools installed)

For 4.6, we can add support for compiling `.metallib` binaries on Windows too, as the Metal Shader Compiler is available as an installable option there too. Perhaps after this WWDC, Apple might even have made it available on Linux 🤞🏻 

--- clayjohn:
@stuartcarnie I see, so on macOS we automatically bake to `.metallib` while on other OSes we still bake to MSL?

--- stuartcarnie:
@clayjohn 

> I see, so on macOS we automatically bake to `.metallib` while on other OSes we still bake to MSL?

That's correct – the generated shader cache will store the baked shader type as either MSL or `.metallib`, so when it's picked up by Godot, it either loads the binary or the MSL source. All seamless for users.



--- Calinou:
> This brings about a question from me. What other features does Godot have (if any) for frontloading things of high computation at export time? If others, a page in the godot book regarding improving load times and performance (if one doesn't exist already) would be really useful

The main remaining aspects are (from most to least impactful in most 3D games):

- Texture streaming.
- Mesh streaming.
- Precompiling visual shaders to text shaders.
- Baking noise textures.
- Baking reflection probes (doesn't actually speed up loading, but avoids pop-in that you may want to hide with a loading screen).

--- TCROC:
> > This brings about a question from me. What other features does Godot have (if any) for frontloading things of high computation at export time? If others, a page in the godot book regarding improving load times and performance (if one doesn't exist already) would be really useful
> 
> The main remaining aspects are (from most to least impactful in most 3D games):
> 
>     * Texture streaming.
> 
>     * Mesh streaming.
> 
>     * Precompiling visual shaders to text shaders.
> 
>     * Baking noise textures.
> 
>     * Baking reflection probes (doesn't actually speed up loading, but avoids pop-in that you may want to hide with a loading screen).

Nice!  And are these things that Godot is capable of doing?  Or features that are planned to be added in?

--- clayjohn:
Folks, please keep comments on topic. It's hard enough to keep track of important info on such a long PR already 

--- Repiteo:
Thanks! Fantastic work on this absolute beast of a PR!

--- DarioSamo:
> Baking for Vulkan can be done from any device, but baking for D3D12 needs to be done from a Windows device (@DarioSamo please confirm)

Correct. This could potentially change in the future if it's figured out how to run the necessary functions from Linux in the future. DXC is available but the root signature generation, not really sure yet. Could potentially be done from DXC too if I remember correctly.

--- kisg:
> @clayjohn
> 
> > I see, so on macOS we automatically bake to `.metallib` while on other OSes we still bake to MSL?
> 
> That's correct – the generated shader cache will store the baked shader type as either MSL or `.metallib`, so when it's picked up by Godot, it either loads the binary or the MSL source. All seamless for users.

I think at the very least this property should be documented, or even better issued a warning at runtime if someone is baking on Windows / Linux where compilation to the Metal IR is not available. In my tests when we first developed Metal baking support, the compilation from SPIR-V to MSL caused only minimal improvements compared to doing everything at loading time.

There are other points, especially on mobile, like distributing baked shaders as (possibly on-demand) asset packs instead of baking them into a PCK. Should we open a new proposal to discuss the details of this?

CC: @stuartcarnie @DarioSamo 

--- stuartcarnie:
> There are other points, especially on mobile, like distributing baked shaders as (possibly on-demand) asset packs instead of baking them into a PCK. Should we open a new proposal to discuss the details of this?

That sounds interesting – would you be able to download `.metallib` binaries and run them on an iOS device? I would wonder if they need to be signed, given they are executable code.

--- kisg:
> > There are other points, especially on mobile, like distributing baked shaders as (possibly on-demand) asset packs instead of baking them into a PCK. Should we open a new proposal to discuss the details of this?
> 
> That sounds interesting – would you be able to download `.metallib` binaries and run them on an iOS device? I would wonder if they need to be signed, given they are executable code.

We are not signing them now, and they work. :)
As you know, all the metallib data is stored in a custom Godot specific container, that is extracted at runtime and loaded from a byte array, so the Metal APIs have no idea where it came from.

So putting the shader cache files into asset packs should be possible without any major changes. The biggest question is: how can we define the dependencies between shaders and other resources at build time so the right shaders go into each asset pack. Also to clarify, on iOS putting "patch PCKs" into asset packs is feasible, unlike on Android, where PCK content access is slow in application and asset bundles.


--- stuartcarnie:
> We are not signing them now, and they work. :) As you know, all the metallib data is stored in a custom Godot specific container, that is extracted at runtime and loaded from a byte array, so the Metal APIs have no idea where it came from.

Of course – and we can compile Metal shaders dynamically at runtime anyhow 👍🏻 

--- DarioSamo:
> There are other points, especially on mobile, like distributing baked shaders as (possibly on-demand) asset packs instead of baking them into a PCK. Should we open a new proposal to discuss the details of this?

Wouldn't it work already just by virtue of having an extra .pck with them?

--- fire:
I am having trouble with permissive errors in my compiler. https://github.com/V-Sekai/godot/actions/runs/15362742009/job/43231897137

```
 Error: ./servers/rendering/rendering_shader_container.h:41:2: error: declaration does not declare anything [-Werror,-Wmissing-declarations]
   41 |         static const uint32_t VERSION;
      |         ^~~~~~~~~~~~~~~~~~~~~
1 error generated.
```

Here my attempt at a patch https://github.com/V-Sekai/godot/commit/71012958ba50ed040e9828454832fc39018d416d

According to git blame `RenderingShaderContainer::MAGIC_NUMBER` and `RenderingShaderContainer::VERSION` were added here.

--- Not-Parker:
Does this feature pave the way for .gdshader source code being omitted from exported games?

--- clayjohn:
> Does this feature pave the way for .gdshader source code being omitted from exported games?

That isn't something that we have discussed. But this PR is necessary if someone were to implement a system to allow omitting .gdshader source code from exported games. 

--- DarioSamo:
> Does this feature pave the way for .gdshader source code being omitted from exported games?

The source code resulting from gdshader is pretty crucial to generating the correct hash, so you'd need to modify that part (changing the input of the hash) to be able to omit it.

--- dsnopek:
After this PR, Godot is crashing for me if the project has any shader that uses `VIEW_INDEX`. I just made issue https://github.com/godotengine/godot/issues/107187 with an MRP and other info

--- jamie-pate:
Feedback from testing this feature in 4.5-dev5:

* Documentation requests:
    * Compatibility matrix? (rendering_methods * rendering_devices)
e.g. `opengl3` has no support
    * It doesn't appear to function with `--headless` (i thought this was [expected to work](https://github.com/godotengine/godot/pull/102552#issuecomment-2648153706)?)
        * It does appear to generate the exported shader cache under xvfb-run for CI
    
    > The shader classes aren't tied to a particular driver running. No GPU is required for the process, as that was part of most of the refactoring that was done to take it out of the drivers and into their own classes that can be used independently.

Features that would make this much more useful:

1) a flag or project setting that displays the shader cache hit/miss statistics somehow
2) `EditorExportPlugin` support for determining the materials that should have shaders precompiled.
    * In my project quality level changes cause new compilations as I disable features for lower hardware targets.
    * These variants could also be precompiled if there was a hook for gdscript code that generates duplicated materials variations.



--- Calinou:
> a flag or project setting that displays the shader cache hit/miss statistics somehow

We can print a message after export that would be displayed in the terminal and the editor Output panel for this.

This would also be a good opportunity to print other statistics about the project export, such as the number of files in the PCK, the PCK's size (useful to know if using embedded PCK) and the total size (binary size + PCK size, or APK/AAB size for Android).

--- jamie-pate:
> We can print a message after export 

I'm more interested in compilations that happen in the exported project because they were _missed_ in shader baking

--- DarioSamo:
Verbose mode currently prints cache misses, so you could definitely add to that spot and add it to a monitor.

--- nubels:
Will the shader baker be added to web exports in the future? I can't find it in the web export properties and I couldn't find this limitation mentioned anywhere.

--- bruvzg:
It's for Forward+/Mobile renderers and web exports are Compatibility only.

--- Calinou:
I've opened a documentation PR, feel free to take a look:

- https://github.com/godotengine/godot-docs/pull/11206

--- Not-Parker:
> > Does this feature pave the way for .gdshader source code being omitted from exported games?
> 
> The source code resulting from gdshader is pretty crucial to generating the correct hash, so you'd need to modify that part (changing the input of the hash) to be able to omit it.

Would it make sense to have "Feature" definitions built-in as part of the Shader resource to be used by the preprocessor?

For example, let's say I have a shader with 3 features. The first two are enable/disable features, the third is an integer feature ranging from 0-2. Feature two depends on feature one (can't be enabled without feature one enabled).

In the shader resource (simple example only, can be done better than this):

```csharp
Dictionary<string, string> BooleanFeatures;
Dictionary<string, int> IntegerFeatures;
```

In the inspector for the shader resource:
Add boolean feature ["FEATURE_ONE", null] // Add feature with no dependencies
Add boolean feature ["FEATURE_TWO", "FEATURE_ONE"] // Add feature that depends on another feature
Add integer feature ["INTEGER_FEATURE", 2] // Add integer feature that accepts values 0-2

In the shader code:

```glsl
#ifdef FEATURE_ONE
// shader code
#endif

#ifdef FEATURE_TWO
// shader code
#endif

#ifdef INTEGER_FEATURE
// shader code
#endif
```

In the inspector for the ShaderMaterial instance:

Set Shader to example shader.
Inspector is populated with checkboxes for Boolean features and fields for integer features.

Now, every possible permutation of the shader (at least from the gdshader perspective) is technically known, and a hash can be generated through a combination of the shader's name or resource path (probably better to have a dedicated name property to support embedded subresource shaders), as well as each each of the shader's features. The hash could probably even be precalcuated and stored on the ShaderMaterial itself as metadata or a dedicated property. 

This may also even allow for easier pre-compilation of all gdshader shaders, as individual ShaderMaterial instances would not be required, since all permutations of the shader are already known and can be iteratively cycled through and compiled to SPIRV for each valid engine shader variant on export.

Whether or not this is a viable solution, not including the source code for game shaders is definitely possible, I'm not aware of any other engines/non-godot games which ship with the raw shader code, especially not AAA games. 


--- clayjohn:
@MarioBossReal See https://github.com/godotengine/godot-proposals/issues/8076 for a proposal that appears to do the same thing you are suggesting. 

--- KeyboardDanni:
Is there some way to confirm that the shader baker is working? Because for my project the exporter doesn't take very long to bake, and startup times in the exported game are as slow as they are in editor with the shader cache cleared.

--- clayjohn:
> Is there some way to confirm that the shader baker is working? Because for my project the exporter doesn't take very long to bake, and startup times in the exported game are as slow as they are in editor with the shader cache cleared.

Ya, just run the executable with verbose mode `--verbose` Shader cache misses will be printed out to the console

--- KeyboardDanni:
Well, I'm getting a bunch of messages about "Loading cache for shader" and I don't see any cache misses. So I guess the benefits just aren't that noticeable on Vulkan. Which is unfortunate, but at least the baker seems to be working.

--- clayjohn:
> Well, I'm getting a bunch of messages about "Loading cache for shader" and I don't see any cache misses. So I guess the benefits just aren't that noticeable on Vulkan. Which is unfortunate, but at least the baker seems to be working.

Did you profile your load times and validate that loading shaders are the slow part? Depending on how many textures/scripts you have, it can be very common to be bottlenecked on Filesystem access

--- KeyboardDanni:
I have a custom shader warmer at the start so I know when shaders need to be compiled. After I clear the shader cache in the graphics drivers and game's app data folder, it takes about 8 seconds for the Godot splash to appear, and 6 seconds for the shader warmer to go through all the necessary shaders. Otherwise each takes less than a quarter of a second.

It's not a *huge* issue, but it is a bit annoying, and for future projects it might increase if I ever write additional custom shaders.

I also doubt filesystem access has a role here, at least in this case. The game's pack file is small enough to fit on an N64 cartridge so it's probably I/O cached by the OS.

--- jamie-pate:
As reported here: #106757 look for MTLCompilerService utilizing all cores on the system while you wait... (Vulkan is still using Metal on MacOS, but it's a lower layer)

<img width="953" height="402" alt="image" src="https://github.com/user-attachments/assets/bec80a20-1322-4c13-aa85-c78d237bbb71" />


--- KeyboardDanni:
On MacOS, yes. In my case I'm talking about native Vulkan on Windows (and by extension, Linux), where shader compilation is done in the driver rather than a centralized system service.

Again, I may have simply misjudged the gains from the shader baker on native Vulkan. https://github.com/godotengine/godot/pull/111452 mentions that `spirv-opt` could be useful for the baker if it can output an IR that takes less time for drivers to optimize. But that seems like a whole 'nother can of worms. Maybe best implemented as a separate tool download to avoid bloating the main editor binary?

--- DarioSamo:
> Well, I'm getting a bunch of messages about "Loading cache for shader" and I don't see any cache misses. So I guess the benefits just aren't that noticeable on Vulkan. Which is unfortunate, but at least the baker seems to be working.

Godot's shader compilation for Vulkan in particular is tuned to be very quick because it doesn't even feature a shader optimizer. Glslang operates as a very quick GLSL -> SPIR-V translator. Backends such as D3D12 and Metal are heavily benefited by the inclusion of the shader baker because they can skip an expensive conversion process from SPIR-V to their own formats. The Vulkan driver doesn't need to do this, so the gains are pretty small.

But as you found out from what https://github.com/godotengine/godot/pull/111452 claims, we could indeed improve the loading times at the driver level if we had said optimizer, which would in turn make the shader compilation time no longer be as quick (think in the order of around a couple of milliseconds to several hundred). The shader baker is basically our scaffolding to be able to now include that in Vulkan without sacrificing big amounts of runtime performance dedicated to shader compilation.


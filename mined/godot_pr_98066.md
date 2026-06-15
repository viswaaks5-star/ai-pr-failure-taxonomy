# PR 98066 [MERGED] — Fix Android mono export with 2 or more cpu architectures fails
AUTHOR: TCROC

## BODY
Fixes: https://github.com/godotengine/godot/issues/98064
*Bugsquad edit:* Fixes #101948 for gradle builds.

When 2 or more architectures are configured for support in an android export, jars per architecture are attempted to be exported.  This is due to mono / dotnet including a jar per cpu architecture.  However, this causes problems because jars are cpu agnostic and result in conflicts during the export process.  Here are some images illustrating the issue:

![image](https://github.com/user-attachments/assets/ed6b5acc-2db0-4b0c-9349-0236fc82003d)

![image](https://github.com/user-attachments/assets/e04547e0-08b8-4d9c-95da-76ca3935f711)

And then when exporting we get:

```
FAILURE: Build failed with an exception.

* What went wrong:
Execution failed for task ':mergeExtDexMonoDebug'.
> A failure occurred while executing com.android.build.gradle.internal.tasks.DexMergingTaskDelegate
   > There was a failure while executing work items
      > A failure occurred while executing com.android.build.gradle.internal.tasks.DexMergingWorkAction
         > com.android.builder.dexing.DexArchiveMergerException: Error while merging dex archives: 
           Learn how to resolve the issue at https://developer.android.com/studio/build/dependencies#duplicate_classes.
           Type net.dot.android.crypto.DotnetProxyTrustManager is defined multiple times: /home/tcroc/dev/BlockyBallOT/blockyball-godot/android/app/build/build/intermediates/external_file_lib_dex_archives/monoDebug/0_jetified-libSystem.Security.Cryptography.Native.Android.jar:classes.dex, /home/tcroc/dev/BlockyBallOT/blockyball-godot/android/app/build/build/intermediates/external_file_lib_dex_archives/monoDebug/2_jetified-libSystem.Security.Cryptography.Native.Android.jar:classes.dex
```

To fix it, I added a HashSet to ExportPlugin.cs that makes sure multiple jars of the same name are not included in the export.

## COMMENTS
--- TCROC:
Hey @raulsntos. Can we add this PR to the 4.4 milestone? Otherwise mono + gradle builds will no longer be possible.

--- TCROC:
@clayjohn Just pinging you to make sure this doesn't get forgotten for 4.4 :).  Its in my fork and its such a small change that I won't have a problem maintaining it.  But it will prevent other devs using mono + dotnet from being able to use android gradle and aab exports.  Which is commonly used for distribution on Google Play so that FAT apk's aren't needed

--- clayjohn:
CC @raulsntos to comment on the Csharp stuff and @m4gr3d to comment on the gradle stuff

--- TCROC:
Hey @clayjohn :)  Can we add this to the 4.4 milestone?  This way it doesn't get forgotten before 4.4 release.  Even if it does get rejected in favor of something else.  It came up on my mind again today and I don't want to get caught up in my other work + lose track of this and then 4.4 ship with Android + mono exports being broken for ".aab" gradle users.  Which is likely most Google Play Store devs.

--- m4gr3d:
@raulsntos Can we close this PR since https://github.com/godotengine/godot/pull/100351 was merged?

--- TCROC:
> @raulsntos Can we close this PR since #100351 was merged?

@raulsntos

Its up to you and the other godot devs.  There is technically still an issue that this PR resolves that the other PR does not.

The issue being keeping an up to date jar for android.  And especially jars for each .NET version.  The current approach requires using the one manually stored in this GitHub repo.  I haven't tested to confirm, but my guess is this likely will not be compatible between dotnet versions and will require regular updating.  Or keeping one stored for each dotnet version godot wants to support.  I still recommend leaving this PR open until either this PR goes through or a different PR goes through similar to this PR that fixes the remaining issue regarding .NET version compatibility.

--- TCROC:
This PR uses the jar microsoft provides in the nuget package.  So its automatically pulled from official Microsoft feeds.  Granted this PR can likely be improved by making sure it grabs the jar associated with the android target.  I don't suspect that would be too hard to add support for.  I just personally don't have time to make changes to this PR as we are getting our game ready for release.  But this PR accomplishes everything except ensuring which jar is chosen based on target abi.

BUT

That may even be a non issue based on my research here: https://github.com/godotengine/godot/pull/98066#discussion_r1803623008

^ And if that research holds true, this PR is good to go and should go through and override the other PR.

At the end of the day, our fork is working so we are happy.  Whatever you guys decide :).  If maintaining our fork becomes too challenging I'll bring more attention to this.

--- raulsntos:
@m4gr3d Looks like the .NET 8 jar we're vendoring of [`System.Security.Cryptography.Native.Android`](https://github.com/godotengine/godot/blob/master/platform/android/java/app/monoLibs/libSystem.Security.Cryptography.Native.Android.jar) is incompatible with .NET 9 (see https://github.com/godotengine/godot/issues/101948#issuecomment-2613682555). This PR would fix that issue for Gradle builds (non-Gradle builds would still be affected though).

--- m4gr3d:
> @m4gr3d Looks like the .NET 8 jar we're vendoring of [`System.Security.Cryptography.Native.Android`](https://github.com/godotengine/godot/blob/master/platform/android/java/app/monoLibs/libSystem.Security.Cryptography.Native.Android.jar) is incompatible with .NET 9 (see [#101948 (comment)](https://github.com/godotengine/godot/issues/101948#issuecomment-2613682555)). This PR would fix that issue for Gradle builds (non-Gradle builds would still be affected though).

Thanks for the context! 
We should go ahead with this approach then to solve the issue for Gradle builds. This would also require that we omit the `jar` file included in the `monoLibs` directory when we generate the gradle templates to avoid conflict with the retrieved `jar` file.

@raulsntos For the non-gradle builds, can we detect the version of .NET being used and show a warning?

--- TCROC:
@raulsntos @m4gr3d I'm glad to hear you guys are leaning towards this approach! :)  We recently finished out load tests so I do have a little bit of capacity now to make some changes to this PR if you want anything changed in order to push it through.

--- TCROC:
hey @m4gr3d @raulsntos Just checking in again to see if there's any adjustments you want me to make on this pr so we can close the issue it will fix :)

--- raulsntos:
> For the non-gradle builds, can we detect the version of .NET being used and show a warning?

Yes, since we now require at least .NET 8 we can use [CLI-based project evaluation](https://learn.microsoft.com/en-us/visualstudio/msbuild/evaluate-items-and-properties).

```bash
dotnet build MyProject.csproj --getProperty:TargetFramework
```

--- TCROC:
> > For the non-gradle builds, can we detect the version of .NET being used and show a warning?
> 
> Yes, since we now require at least .NET 8 we can use [CLI-based project evaluation](https://learn.microsoft.com/en-us/visualstudio/msbuild/evaluate-items-and-properties).
> 
> ```shell
> dotnet build MyProject.csproj --getProperty:TargetFramework
> ```

Is this something you would like me to do in this PR?  If so, how do I go about doing this?

And another question while I'm at it, do we need to make any changes now that the other PR that handles jars is in?  Will this PR's logic conflict with that PR's logic during the export process?  PR in question here: https://github.com/godotengine/godot/pull/100351

--- raulsntos:
> do we need to make any changes now that the other PR that handles jars is in?

We'll want to revert the changes to `build.gradle`, so the jar is only include in the export templates but not in gradle builds.

> > ```
> > dotnet build MyProject.csproj --getProperty:TargetFramework
> > ```
> Is this something you would like me to do in this PR? If so, how do I go about doing this?

I think it can be done in a follow-up PR, but feel free to do it here if you want. Here's how you could execute the command:

```C++
String pipe;
List<String> args;
args.push_back("build");
args.push_back(project_path);
args.push_back("--getProperty:TargetFramework");

int exitcode;
Error err = OS::get_singleton()->execute("dotnet", args, &pipe, &exitcode, true);

if (err != OK) {
    WARN_PRINT("Failed to execute dotnet command. Error " + error_names[err]);
} else if(exitcode != 0) {
    print_line(pipe);
    WARN_PRINT("dotnet command exited with code " + itos(exitcode) + ". See output above for more details.");
} else {
    String tfm = pipe.strip_edges();
    if (tfm != "net8.0") {
        err += TTR("Project targets '" + tfm + "' but the export template only supports 'net8.0'. Consider using gradle builds instead.");
    }
}
```

And you'd want to execute this somewhere around here: https://github.com/godotengine/godot/blob/0b6a717ac17f1d6bd7963740cf2c2128b36ff7aa/platform/android/export/export_plugin.cpp#L2534-L2537

--- TCROC:
> > do we need to make any changes now that the other PR that handles jars is in?
> 
> We'll want to revert the changes to `build.gradle`, so the jar is only include in the export templates but not in gradle builds.

Do you simply want me to revert this build.gradle back to what it was before?

https://github.com/godotengine/godot/pull/100351/files#diff-81aadb220697f9a3dac1980c60648954b1982b9c19cd3629a57c0508dd5b3653


--- raulsntos:
Yes, and move the `.jar` file back to `/modules/mono/thirdparty`.

--- TCROC:
> Yes, and move the `.jar` file back to `/modules/mono/thirdparty`.

Done 😎.  I'll leave your other suggestion about a warning for a follow up PR from someone who's more familiar on how to implement it.

Would you like me to make any other changes to this PR?

--- TCROC:
> One small cleanup remaining and the PR is good to go!

Perfect! I'll clean this up tomorrow! :)

--- Repiteo:
Thanks!


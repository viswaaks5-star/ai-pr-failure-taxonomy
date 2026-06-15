# PR 113284 [MERGED] — Add BoneTwistDisperser3D to propagate IK target's twist
AUTHOR: TokageItLab

## BODY
Add BoneTwistDisperser3D.

As commented in https://github.com/godotengine/godot/pull/110120#issuecomment-3536557629, using BoneConstraints can provide a solution for propagating twist to the parent to some extent. However, in cases where the twist axis does not align with the XYZ basis, the solution is not as straightforward. Furthermore, since the canceled twist must be applied to the target itself, it is not easy to use for not advanced users.

This allows them to automate these processes by creating a chain. Of course, it can be used even without IK.

https://github.com/user-attachments/assets/e4b3e996-27b8-49e1-9809-dd495586ac2c

[ik_test_match_target.zip](https://github.com/user-attachments/files/23826399/ik_test_match_target.zip)



## COMMENTS
--- TokageItLab:
There is request for a curve editor from @lyuma, so now it is implemented.

Thereby, twist weight has been changed to twist amount without normalization. Also, it has been added to the documentation that the auto assigning amount except for DISPERSE_MODE_CUSTOM are monotonically increasing.

<img width="868" height="844" alt="image" src="https://github.com/user-attachments/assets/0726e54d-7ef5-4c93-9f80-f6be0cdc2c2d" />

Whether twist_amount is read-only depends on the existence of the Curve resource.

---

**Can be considered the future follow up**

The horizontal axis of the curve currently represents the index rather than the bone length, but since this implementation is the same as SpringBoneSimulator3D, it could be improved as a follow-up in the future .

The same applies to improvements for extracting twists greater than 180 degrees; this should be fixed at the same time as ConvertTransformModifier3D.

--- TokageItLab:
As I've mentioned several times before, the IKModifier itself only changes the joint placement/rotation using only Swing , without Twist. So these modules for the twist may become that IK enhancement as option.

For example, it should be interesting to see how the behavior of IK can be quite varied due to configuration differences like the following:

---

- Simple non-deterministic FABRIK:

<img width="209" height="131" alt="image" src="https://github.com/user-attachments/assets/d621fdc5-03c4-475f-8bb5-2c2a283e6e51" />

https://github.com/user-attachments/assets/ebf1a84c-f5a0-4843-a449-4cda32071e58

---

- Pre-twist the root using aim
- Further pre-twist the target and then sparse
- Finally, performing deterministic FABRIK can stabilize the bend direction to some extent

<img width="227" height="197" alt="image" src="https://github.com/user-attachments/assets/c35c382d-150d-407b-ad0b-0e1e24398461" />

https://github.com/user-attachments/assets/23ee0ae9-5b0d-42ea-a5a7-b0cb20347c22

[ik_combination.zip](https://github.com/user-attachments/files/23835289/ik_combination.zip)

In other words, a rich IK component has these nodes as member options (like bool to call internal function) for IK.

However, since these calculations are also useful outside of IK, having them as separate nodes makes sense IMO. Especially when using custom IK, reusability is a big benefit. Although we will need to prepare several tutorials and demos later on - or we can provide a wrapper component as an addon to automate these configurations.

--- fire:
In a discord conversation we discussed the issue of order problem -- like pre-ik mnodifiers vs post-ik modifiers solving causing incorrect results.

A resolution is to use documentation as a workaround by [documenting](https://github.com/godotengine/godot-docs) placing the CopyConstraint and TwistDisperse before IK. If we ultimately need the tip to face the target, we can apply CopyConstraint again after IK. See https://github.com/godotengine/godot/pull/113284#issuecomment-3591855270 demo.

--- TokageItLab:
In practice, whether to apply IK before or after depends on the specific use case.

For example, if you want to apply a Twist constraint to IK,
first perform unrestricted Twist using CopyTransform+Target and TwistDisperser, then either use RotationAxis in IK afterward, or restrict the Twist range before IK using ConvertConstraint or similar. Finally, depending on how you want the tip to orient toward the target, use CopyTransform or AimModifier after IK. In some cases, users may need to add additional twist restrictions here.

For simpler cases, such as twisting tentacles or vines, using TwistDisperser after IK alone is sufficient.

However, these are examples for combining with IK and are off-topic for discussions about the TwistDisperser API itself. TwistDisperser is purely a node that mathematically dissipates and distributes twist along a chain.

--- TokageItLab:
Tweaked icon to reduced usage by removing unnecessary points. Appearance remains unchanged.

--- GeorgeS2019:
@lyuma 

I went through all possible min godot project to demonstrate each use cases of the 8 subclasses of **SkeletonModifier3D**

I also went through the video that comes with the minimum godot project (zip), usually the provided test min Godot Project is not the complete project as shown by the provided video.

It would be great if we have godot project that correclate with the provided image or video so users could start experiment with these 8 new subclasses.

I also check the youtube and ask ChatGPT, many users struggles how to use the SkeletonModifier3D. The list of youtube video are found on the link below 

---
follow further discussion of godot demo on 3D IK [here](https://github.com/godotengine/godot-demo-projects/pull/1271#issuecomment-3601042472)

--- akien-mga:
Thanks!


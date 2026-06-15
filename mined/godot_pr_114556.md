# PR 114556 [MERGED] — Add ping-pong playback support to SpriteFrames / AnimatedSprite2D / AnimatedSprite3D
AUTHOR: jgill88

## BODY
Closes https://github.com/godotengine/godot-proposals/issues/11698.

Adds a Ping Pong option to SpriteFrames that marks the selected SpriteFrames animation as looping in ping-pong mode. When selected, AnimatedSprite2D and AnimatedSprite3D play the animation in ping-pong mode.

<img width="347" height="122" alt="image" src="https://github.com/user-attachments/assets/6d747171-3cfa-4970-b6d0-cd3286a17c85" />



## COMMENTS
--- kleonc:
Hey @jgill88, are you planning to work further on this PR?
I agree with https://github.com/godotengine/godot/pull/114556#discussion_r2867584328, the loop/ping-pong bools should be changed to a single enum property. UI-wise I think a single button with a list of options would make sense, something like in AnimationPlayer:

https://github.com/user-attachments/assets/643c87c4-288f-4b5c-8820-77679377f074



--- jgill88:
> Hey @jgill88, are you planning to work further on this PR? I agree with [#114556 (comment)](https://github.com/godotengine/godot/pull/114556#discussion_r2867584328), the loop/ping-pong bools should be changed to a single enum property. UI-wise I think a single button with a list of options would make sense, something like in AnimationPlayer:
> 
>  Godot_v4.6.1-stable_win64_yR2tUPdNEt.mp4

Yes! I plan to address the feedback in the next day or two. I’ll give you a shout if I have questions. 

--- jgill88:
> Hey @jgill88, are you planning to work further on this PR? I agree with [#114556 (comment)](https://github.com/godotengine/godot/pull/114556#discussion_r2867584328), the loop/ping-pong bools should be changed to a single enum property. UI-wise I think a single button with a list of options would make sense, something like in AnimationPlayer:
> 
>  Godot_v4.6.1-stable_win64_yR2tUPdNEt.mp4

hey @kleonc thanks for the UI feedback, I've gone ahead and made those adjustments to include switching over to a LoopMode enum, and a menu similar to the AnimationPlayer dropdowns (and a rebase). 

I'm not totally in love with the iconography here - I wanted the button to show a "loop" icon even when LoopMode::LOOP_NONE, to indicate to the user that it's the loop settings menu, so I went with:

LOOP_NONE: 
- Loop icon
- Unpressed button

LOOP_LINEAR:
- Loop icon
- Pressed button

LOOP_PINGPONG:
- PingPong icon
- Pressed button. 

https://github.com/user-attachments/assets/cb01e521-cd11-4332-bd61-d269a64ada63

Let me know if you have any feedback there, happy to adjust.

--- AThousandShips:
I think the solution should break compatibility only if necessary, and provide as smooth a migration path as possible

I'd suggest keeping the old property and methods as deprecated and adding new methods and a new property, with the old property doing the same functionality as the compat bind does translating to the enum

I don't think GDScript does automatic casting from `bool` to `int` to begin with, but especially not `bool` to a specific enum, but I haven't tested this, I also don't know if it will work correctly in C# or c++ with godot-cpp (the compat binds do *not* provide backwards compatibility for *new* code using the *new* API dump, it only provides binary compatibility for extensions built with an older API version)

Also we can't make any assumptions of other bindings using the extension system and whether they allow casting from `bool` to this specific enum, any one of those could break with this if they don't (we assume default arguments are supported universally, and that Godot types cast in certain ways, like `String` to `StringName` and vice versa, but nothing else)

--- kleonc:
> I'm not totally in love with the iconography here - I wanted the button to show a "loop" icon even when LoopMode::LOOP_NONE, to indicate to the user that it's the loop settings menu, so I went with:
> 
> LOOP_NONE:
>   * Loop icon
>   * Unpressed button
> 
> LOOP_LINEAR:
>   * Loop icon
>   * Pressed button
> 
> LOOP_PINGPONG:
>   * PingPong icon
>   * Pressed button.

Makes sense... that's exactly how the AnimationPlayer indicates that. 😄 However, note that it doesn't show a dropdown, it uses a 3-value-toggle instead:

https://github.com/user-attachments/assets/fdd1b9c6-d4f5-436a-a9d3-3f0c0fae4e20

While the dropdown is clearer, if you're already familiar with this option, it's faster to click the toggle 1 or 2 times to change the default loop mode than to click and choose an option from the dropdown (I've realized this while testing now). So I think we should probably go with the toggle here, removing the dropdown.
For 4+ modes to choose from dropdown would for sure be better, but for 3 a toggle makes sense (+it's consistent with the AnimationPlayer).

---

> Let me know if you have any feedback there, happy to adjust.

Regarding the bool to enum change, we don't want to unnecessarily break the compatibility (I've discussed it briefly with other maintainers). Instead of changing the existing bool getter/setter, adding a new getter/setter using the enum is preferred.

(oh, others already chimed in 😄)

<details><summary>Here's a diff with my suggested compatibility related changes (click to expand)</summary>
<p>

```diff
diff --git a/doc/classes/SpriteFrames.xml b/doc/classes/SpriteFrames.xml
index bbab20001b..dc0a9cba19 100644
--- a/doc/classes/SpriteFrames.xml
+++ b/doc/classes/SpriteFrames.xml
@@ -47,7 +47,14 @@
 				Duplicates the animation [param anim_from] to a new animation named [param anim_to]. Fails if [param anim_to] already exists, or if [param anim_from] does not exist.
 			</description>
 		</method>
-		<method name="get_animation_loop" qualifiers="const">
+		<method name="get_animation_loop" qualifiers="const" deprecated="Use [method get_animation_loop_mode] instead.">
+			<return type="bool" />
+			<param index="0" name="anim" type="StringName" />
+			<description>
+				Returns [code]true[/code] if [code]get_animation_loop_mode(anim) == LOOP_LINEAR[/code]. Otherwise, returns [code]false[/code].
+			</description>
+		</method>
+		<method name="get_animation_loop_mode" qualifiers="const">
 			<return type="int" enum="SpriteFrames.LoopMode" />
 			<param index="0" name="anim" type="StringName" />
 			<description>
@@ -124,12 +131,21 @@
 				Changes the [param anim] animation's name to [param newname].
 			</description>
 		</method>
-		<method name="set_animation_loop">
+		<method name="set_animation_loop" deprecated="Use [method set_animation_loop_mode] instead.">
+			<return type="void" />
+			<param index="0" name="anim" type="StringName" />
+			<param index="1" name="loop" type="bool" />
+			<description>
+				If [param loop] is [code]false[/code] equivalent to [code]set_animation_loop_mode(LOOP_NONE)[/code].
+				If [param loop] is [code]true[/code] equivalent to [code]set_animation_loop_mode(LOOP_LINEAR)[/code].
+			</description>
+		</method>
+		<method name="set_animation_loop_mode">
 			<return type="void" />
 			<param index="0" name="anim" type="StringName" />
-			<param index="1" name="loop" type="int" enum="SpriteFrames.LoopMode" />
+			<param index="1" name="loop_mode" type="int" enum="SpriteFrames.LoopMode" />
 			<description>
-				Sets the [param loop] mode for the [param anim] animation.
+				Sets the [param loop_mode] for the [param anim] animation.
 			</description>
 		</method>
 		<method name="set_animation_speed">
diff --git a/editor/scene/sprite_frames_editor_plugin.cpp b/editor/scene/sprite_frames_editor_plugin.cpp
index d328b6b526..5bfe93b0e9 100644
--- a/editor/scene/sprite_frames_editor_plugin.cpp
+++ b/editor/scene/sprite_frames_editor_plugin.cpp
@@ -1374,7 +1374,7 @@ void SpriteFramesEditor::_animation_loop_changed(int p_index) {
 	EditorUndoRedoManager *undo_redo = EditorUndoRedoManager::get_singleton();
 
 	SpriteFrames::LoopMode to_loop = SpriteFrames::LoopMode::LOOP_NONE;
-	SpriteFrames::LoopMode from_loop = frames->get_animation_loop(edited_anim);
+	SpriteFrames::LoopMode from_loop = frames->get_animation_loop_mode(edited_anim);
 
 	switch (p_index) {
 		case MENU_LOOP_LOOP: {
@@ -1637,7 +1637,7 @@ void SpriteFramesEditor::_update_anim_loop_button() {
 		return;
 	}
 
-	SpriteFrames::LoopMode loop = frames->get_animation_loop(edited_anim);
+	SpriteFrames::LoopMode loop = frames->get_animation_loop_mode(edited_anim);
 	anim_loop->set_pressed_no_signal(loop != SpriteFrames::LoopMode::LOOP_NONE);
 
 	switch (loop) {
@@ -2852,7 +2852,7 @@ Ref<ClipboardAnimation> ClipboardAnimation::from_sprite_frames(const Ref<SpriteF
 	clipboard_anim.instantiate();
 	clipboard_anim->name = p_anim;
 	clipboard_anim->speed = p_frames->get_animation_speed(p_anim);
-	clipboard_anim->loop = p_frames->get_animation_loop(p_anim);
+	clipboard_anim->loop = p_frames->get_animation_loop_mode(p_anim);
 
 	int frame_count = p_frames->get_frame_count(p_anim);
 	for (int i = 0; i < frame_count; ++i) {
diff --git a/misc/extension_api_validation/4.6-stable/GH-114556.txt b/misc/extension_api_validation/4.6-stable/GH-114556.txt
deleted file mode 100644
index 5188225f37..0000000000
--- a/misc/extension_api_validation/4.6-stable/GH-114556.txt
+++ /dev/null
@@ -1,7 +0,0 @@
-GH-114556
---------------
-
-Validate extension JSON: Error: Field 'classes/SpriteFrames/methods/set_animation_loop/arguments/1': type changed value in new API, from "bool" to "enum::SpriteFrames.LoopMode".
-Validate extension JSON: Error: Field 'classes/SpriteFrames/methods/get_animation_loop/return_value': type changed value in new API, from "bool" to "enum::SpriteFrames.LoopMode".
-
-Expanded SpriteFrames to support PingPong looping mode. Changed bool loop enabled to enum.
diff --git a/scene/2d/animated_sprite_2d.cpp b/scene/2d/animated_sprite_2d.cpp
index 7e280b502f..c80f300a35 100644
--- a/scene/2d/animated_sprite_2d.cpp
+++ b/scene/2d/animated_sprite_2d.cpp
@@ -219,7 +219,7 @@ void AnimatedSprite2D::_notification(int p_what) {
 					// Forwards.
 					if (frame_progress >= 1.0) {
 						if (frame >= last_frame) {
-							SpriteFrames::LoopMode loop = frames->get_animation_loop(animation);
+							SpriteFrames::LoopMode loop = frames->get_animation_loop_mode(animation);
 							if (loop == SpriteFrames::LoopMode::LOOP_NONE) {
 								frame = last_frame;
 								pause();
@@ -250,7 +250,7 @@ void AnimatedSprite2D::_notification(int p_what) {
 					// Backwards.
 					if (frame_progress <= 0) {
 						if (frame <= 0) {
-							SpriteFrames::LoopMode loop = frames->get_animation_loop(animation);
+							SpriteFrames::LoopMode loop = frames->get_animation_loop_mode(animation);
 							if (loop == SpriteFrames::LoopMode::LOOP_NONE) {
 								frame = 0;
 								pause();
diff --git a/scene/3d/sprite_3d.cpp b/scene/3d/sprite_3d.cpp
index f30419afd5..cee23c26ca 100644
--- a/scene/3d/sprite_3d.cpp
+++ b/scene/3d/sprite_3d.cpp
@@ -1154,7 +1154,7 @@ void AnimatedSprite3D::_notification(int p_what) {
 					// Forwards.
 					if (frame_progress >= 1.0) {
 						if (frame >= last_frame) {
-							SpriteFrames::LoopMode loop = frames->get_animation_loop(animation);
+							SpriteFrames::LoopMode loop = frames->get_animation_loop_mode(animation);
 							if (loop == SpriteFrames::LoopMode::LOOP_NONE) {
 								frame = last_frame;
 								pause();
@@ -1184,7 +1184,7 @@ void AnimatedSprite3D::_notification(int p_what) {
 					// Backwards.
 					if (frame_progress <= 0) {
 						if (frame <= 0) {
-							SpriteFrames::LoopMode loop = frames->get_animation_loop(animation);
+							SpriteFrames::LoopMode loop = frames->get_animation_loop_mode(animation);
 							if (loop == SpriteFrames::LoopMode::LOOP_NONE) {
 								frame = 0;
 								pause();
diff --git a/scene/resources/sprite_frames.compat.inc b/scene/resources/sprite_frames.compat.inc
deleted file mode 100644
index 65c8a5f09a..0000000000
--- a/scene/resources/sprite_frames.compat.inc
+++ /dev/null
@@ -1,54 +0,0 @@
-/**************************************************************************/
-/*  sprite_frames.compat.inc                                              */
-/**************************************************************************/
-/*                         This file is part of:                          */
-/*                             GODOT ENGINE                               */
-/*                        https://godotengine.org                         */
-/**************************************************************************/
-/* Copyright (c) 2014-present Godot Engine contributors (see AUTHORS.md). */
-/* Copyright (c) 2007-2014 Juan Linietsky, Ariel Manzur.                  */
-/*                                                                        */
-/* Permission is hereby granted, free of charge, to any person obtaining  */
-/* a copy of this software and associated documentation files (the        */
-/* "Software"), to deal in the Software without restriction, including    */
-/* without limitation the rights to use, copy, modify, merge, publish,    */
-/* distribute, sublicense, and/or sell copies of the Software, and to     */
-/* permit persons to whom the Software is furnished to do so, subject to  */
-/* the following conditions:                                              */
-/*                                                                        */
-/* The above copyright notice and this permission notice shall be         */
-/* included in all copies or substantial portions of the Software.        */
-/*                                                                        */
-/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,        */
-/* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF     */
-/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. */
-/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY   */
-/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,   */
-/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE      */
-/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                 */
-/**************************************************************************/
-
-#ifndef DISABLE_DEPRECATED
-
-#include "sprite_frames.h"
-
-#include "core/object/class_db.h"
-
-void SpriteFrames::_set_animation_loop_114556(const StringName &p_anim, bool p_loop) {
-	if (p_loop) {
-		set_animation_loop(p_anim, LoopMode::LOOP_LINEAR);
-	} else {
-		set_animation_loop(p_anim, LoopMode::LOOP_NONE);
-	}
-}
-
-bool SpriteFrames::_get_animation_loop_114556(const StringName &p_anim) const {
-	return get_animation_loop(p_anim) != LoopMode::LOOP_NONE;
-}
-
-void SpriteFrames::_bind_compatibility_methods() {
-	ClassDB::bind_compatibility_method(D_METHOD("set_animation_loop", "anim", "loop"), &SpriteFrames::_set_animation_loop_114556);
-	ClassDB::bind_compatibility_method(D_METHOD("get_animation_loop", "anim"), &SpriteFrames::_get_animation_loop_114556);
-}
-
-#endif // DISABLE_DEPRECATED
diff --git a/scene/resources/sprite_frames.cpp b/scene/resources/sprite_frames.cpp
index 5718b6d816..ad918a8b66 100644
--- a/scene/resources/sprite_frames.cpp
+++ b/scene/resources/sprite_frames.cpp
@@ -29,7 +29,6 @@
 /**************************************************************************/
 
 #include "sprite_frames.h"
-#include "sprite_frames.compat.inc"
 
 #include "core/object/class_db.h"
 #include "scene/scene_string_names.h"
@@ -155,13 +154,23 @@ double SpriteFrames::get_animation_speed(const StringName &p_anim) const {
 	return E->value.speed;
 }
 
-void SpriteFrames::set_animation_loop(const StringName &p_anim, LoopMode p_loop) {
+#ifndef DISABLE_DEPRECATED
+void SpriteFrames::set_animation_loop(const StringName &p_anim, bool p_loop) {
+	set_animation_loop_mode(p_anim, p_loop ? LOOP_LINEAR : LOOP_NONE);
+}
+
+bool SpriteFrames::get_animation_loop(const StringName &p_anim) const {
+	return get_animation_loop_mode(p_anim) == LOOP_LINEAR;
+}
+#endif
+
+void SpriteFrames::set_animation_loop_mode(const StringName &p_anim, LoopMode p_loop_mode) {
 	HashMap<StringName, Anim>::Iterator E = animations.find(p_anim);
 	ERR_FAIL_COND_MSG(!E, "Animation '" + String(p_anim) + "' doesn't exist.");
-	E->value.loop = p_loop;
+	E->value.loop = p_loop_mode;
 }
 
-SpriteFrames::LoopMode SpriteFrames::get_animation_loop(const StringName &p_anim) const {
+SpriteFrames::LoopMode SpriteFrames::get_animation_loop_mode(const StringName &p_anim) const {
 	HashMap<StringName, Anim>::ConstIterator E = animations.find(p_anim);
 	ERR_FAIL_COND_V_MSG(!E, LoopMode::LOOP_NONE, "Animation '" + String(p_anim) + "' doesn't exist.");
 	return E->value.loop;
@@ -209,17 +218,10 @@ void SpriteFrames::_set_animations(const Array &p_animations) {
 		Array frames = d["frames"];
 		Variant loop = d["loop"];
 		if (loop.get_type() == Variant::BOOL) {
-			// backwards compatibility with saved bool loop values.
-			anim.loop = loop ? LoopMode::LOOP_LINEAR : LoopMode::LOOP_NONE;
+			// Backwards compatibility with saved bool loop values.
+			anim.loop = (bool)loop ? LoopMode::LOOP_LINEAR : LoopMode::LOOP_NONE;
 		} else if (loop.get_type() == Variant::INT) {
-			int loop_val = (int)loop;
-
-			if (loop_val < 0) {
-				loop_val = 0;
-			} else if (loop_val > 2) {
-				loop_val = 2;
-			}
-			anim.loop = LoopMode(loop_val);
+			anim.loop = LoopMode(CLAMP((int)loop, LOOP_NONE, LOOP_PINGPONG));
 		}
 
 		for (int j = 0; j < frames.size(); j++) {
@@ -277,8 +279,13 @@ void SpriteFrames::_bind_methods() {
 	ClassDB::bind_method(D_METHOD("set_animation_speed", "anim", "fps"), &SpriteFrames::set_animation_speed);
 	ClassDB::bind_method(D_METHOD("get_animation_speed", "anim"), &SpriteFrames::get_animation_speed);
 
+#ifndef DISABLE_DEPRACETED
 	ClassDB::bind_method(D_METHOD("set_animation_loop", "anim", "loop"), &SpriteFrames::set_animation_loop);
 	ClassDB::bind_method(D_METHOD("get_animation_loop", "anim"), &SpriteFrames::get_animation_loop);
+#endif
+
+	ClassDB::bind_method(D_METHOD("set_animation_loop_mode", "anim", "loop_mode"), &SpriteFrames::set_animation_loop_mode);
+	ClassDB::bind_method(D_METHOD("get_animation_loop_mode", "anim"), &SpriteFrames::get_animation_loop_mode);
 
 	ClassDB::bind_method(D_METHOD("add_frame", "anim", "texture", "duration", "at_position"), &SpriteFrames::add_frame, DEFVAL(1.0), DEFVAL(-1));
 	ClassDB::bind_method(D_METHOD("set_frame", "anim", "idx", "texture", "duration"), &SpriteFrames::set_frame, DEFVAL(1.0));
diff --git a/scene/resources/sprite_frames.h b/scene/resources/sprite_frames.h
index ad98adff39..da4a1e291c 100644
--- a/scene/resources/sprite_frames.h
+++ b/scene/resources/sprite_frames.h
@@ -42,7 +42,6 @@ public:
 		LOOP_NONE,
 		LOOP_LINEAR,
 		LOOP_PINGPONG,
-		// loading sprite frame loop mode clamped from 0-2 in _set_animations
 	};
 
 private:
@@ -64,11 +63,6 @@ private:
 
 protected:
 	static void _bind_methods();
-#ifndef DISABLE_DEPRECATED
-	void _set_animation_loop_114556(const StringName &p_anim, bool p_loop);
-	bool _get_animation_loop_114556(const StringName &p_anim) const;
-	static void _bind_compatibility_methods();
-#endif
 
 public:
 	void add_animation(const StringName &p_anim);
@@ -83,8 +77,13 @@ public:
 	void set_animation_speed(const StringName &p_anim, double p_fps);
 	double get_animation_speed(const StringName &p_anim) const;
 
-	void set_animation_loop(const StringName &p_anim, LoopMode p_loop);
-	LoopMode get_animation_loop(const StringName &p_anim) const;
+#ifndef DISABLE_DEPRECATED
+	void set_animation_loop(const StringName &p_anim, bool p_loop);
+	bool get_animation_loop(const StringName &p_anim) const;
+#endif
+
+	void set_animation_loop_mode(const StringName &p_anim, LoopMode p_loop_mode);
+	LoopMode get_animation_loop_mode(const StringName &p_anim) const;
 
 	void add_frame(const StringName &p_anim, const Ref<Texture2D> &p_texture, float p_duration = 1.0, int p_at_pos = -1);
 	void set_frame(const StringName &p_anim, int p_idx, const Ref<Texture2D> &p_texture, float p_duration = 1.0);
diff --git a/tests/scene/test_sprite_frames.cpp b/tests/scene/test_sprite_frames.cpp
index b8634c5b36..5a162f449e 100644
--- a/tests/scene/test_sprite_frames.cpp
+++ b/tests/scene/test_sprite_frames.cpp
@@ -169,37 +169,37 @@ TEST_CASE("[SpriteFrames] Animation Speed getter and setter") {
 			"Sets animation to zero");
 }
 
-TEST_CASE("[SpriteFrames] Animation Loop getter and setter") {
+TEST_CASE("[SpriteFrames] Animation Loop Mode getter and setter") {
 	SpriteFrames frames;
 
 	frames.add_animation(test_animation_name);
 
 	CHECK_MESSAGE(
-			frames.get_animation_loop(test_animation_name) == SpriteFrames::LoopMode::LOOP_LINEAR,
-			"Sets new animation to default loop value (linear).");
+			frames.get_animation_loop_mode(test_animation_name) == SpriteFrames::LoopMode::LOOP_LINEAR,
+			"Sets new animation to default loop mode value (linear).");
 
 	frames.set_animation_loop(test_animation_name, SpriteFrames::LoopMode::LOOP_LINEAR);
 
 	CHECK_MESSAGE(
-			frames.get_animation_loop(test_animation_name) == SpriteFrames::LoopMode::LOOP_LINEAR,
-			"Sets animation loop to linear");
+			frames.get_animation_loop_mode(test_animation_name) == SpriteFrames::LoopMode::LOOP_LINEAR,
+			"Sets animation loop mode to linear");
 
-	frames.set_animation_loop(test_animation_name, SpriteFrames::LoopMode::LOOP_PINGPONG);
+	frames.set_animation_loop_mode(test_animation_name, SpriteFrames::LoopMode::LOOP_PINGPONG);
 
 	CHECK_MESSAGE(
 			frames.get_animation_loop(test_animation_name) == SpriteFrames::LoopMode::LOOP_PINGPONG,
-			"Sets animation loop to ping pong");
+			"Sets animation loop mode to ping pong");
 
-	frames.set_animation_loop(test_animation_name, SpriteFrames::LoopMode::LOOP_NONE);
+	frames.set_animation_loop_mode(test_animation_name, SpriteFrames::LoopMode::LOOP_NONE);
 
 	CHECK_MESSAGE(
-			frames.get_animation_loop(test_animation_name) == SpriteFrames::LoopMode::LOOP_NONE,
-			"Sets animation loop to none");
+			frames.get_animation_loop_mode(test_animation_name) == SpriteFrames::LoopMode::LOOP_NONE,
+			"Sets animation loop mode to none");
 
 	// These error handling cases should not crash.
 	ERR_PRINT_OFF;
-	frames.get_animation_loop("This does not exist");
-	frames.set_animation_loop("This does not exist", SpriteFrames::LoopMode::LOOP_NONE);
+	frames.get_animation_loop_mode("This does not exist");
+	frames.set_animation_loop_mode("This does not exist", SpriteFrames::LoopMode::LOOP_NONE);
 	ERR_PRINT_ON;
 }
```

</p>
</details> 

--- jgill88:
No problem, I should have double checked before breaking compat! I’ll adjust today. 

--- jgill88:
I like the 3-way-toggle much better than the dropdown menu!

Updated to remove compatibility breakage & switched over the the 3 way toggle. I will squash if/when this PR is accepted!

--- jgill88:
thanks! squashed. 

separately: while in here, i noticed that AnimatedSprite3D and AnimatedSprite2D share a _surprising_ amount of copied/pasted code, they're almost clones of each other :D

i'd be happy to follow this on with a deduplication effort if that's something desired. i saw some musings of more complicated looping in various proposals, and if that were to move forward, deduplication would be a win.

--- jgill88:
~~hmm, not sure why CI is failing for linux/editor mono - is it just flake?~~

> ~~ERROR: Cannot open resource pack '/tmp/test_project.pck'.~~

nvm, looks like it was flake

--- kleonc:
> thanks! squashed.

@jgill88  And thanks to you too! 🙂

> separately: while in here, i noticed that AnimatedSprite3D and AnimatedSprite2D share a _surprising_ amount of copied/pasted code, they're almost clones of each other :D
> 
> i'd be happy to follow this on with a deduplication effort if that's something desired. i saw some musings of more complicated looping in various proposals, and if that were to move forward, deduplication would be a win.

Personally I'm not sure if that's needed/desired. The current state is not awful, and by deduplicating everything it's easy to overengineer.
If anything, it would need to handle only the playback related stuff as it should be common, so for deduplication you'd probably add a class like AnimatedSpritePlayback. This might indeed make editing/adding stuff there easier, but it would also add 2 new files and some indirection in the AnimatedSprites code. Hence I'm not convinced about it.
(I'll forward this question of yours to other maintainers, so _maybe_ you'll get another opinion or even a more "official" statement. But IIRC the general recommendation is to firstly focus on fixing bugs etc. rather than refactoring the code etc.)

BTW I remember deduplicating some Sprite3D/AnimatedSprite3D drawing code myself as a part of #66064, but they at least both extend SpriteBase3D so it was only a matter of factoring out the duplicated code into a helper function in the base class, which was straightforward.
(end of offtopic from me)

---

Also could you please update the [PR description](https://github.com/godotengine/godot/pull/114556#issue-3777925109)? If this PR will be merged and listed in the change log, it's usually what the users refer to when checking out the PR. So an outdated description often leads to user confusion / misinformation (e.g. they could look for a separate ping-pong toggle like it's shown in the outdated image there).
Contributors/reviewers also usually refer to the PR description first.

--- jgill88:
Updated!

--- 

Thanks for the commentary re:dedupe. I was actually enjoying your ascii art when reading the code earlier!

--- Repiteo:
Thanks! Congratulations on your first merged contribution! 🎉 


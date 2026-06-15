# PR 119483 [CLOSED] — Add --log-format=json and --inspect-scene for headless automation
AUTHOR: genno-whittlery

## BODY
Two small, additive command-line flags aimed at the headless / agentic-automation use case described in proposal [#13048](https://github.com/godotengine/godot-proposals/issues/13048), and following the same shape as proposal [#4958](https://github.com/godotengine/godot-proposals/issues/4958).

Both flags are opt-in — default behavior is unchanged.

## 1. `--log-format <text|json>`

Addresses [godot-proposals#13048](https://github.com/godotengine/godot-proposals/issues/13048).

When `json` is selected, every log line on stdout becomes a single newline-delimited JSON record:

\`\`\`bash
godot --headless --log-format json --script my_script.gd
\`\`\`

Output schema:
- info / print: \`{\"ts\",\"level\":\"info\",\"msg\"}\`
- errors / warnings: \`{\"ts\",\"level\",\"function\",\"file\",\"line\",\"code\",\"rationale\",\"editor_notify\",\"backtrace\"?}\`

\`level\` ∈ \`info | error | warning | script_error | shader_error\`.

This gives CI runners and automation tools machine-readable parser/compiler errors with file/line/rationale, which is currently the main pain point in #13048 (\"errors are not consistently structured and often lack file names, line numbers, and clear error boundaries\").

Implementation: a new \`JSONLogger : public Logger\` in \`core/io/logger.{h,cpp}\`, swapped in via a small \`OS::reset_logger()\` helper when the CLI flag is parsed in \`main.cpp\`. The default StdLogger path is untouched.

## 2. \`--inspect-scene <path>\`

Sibling of [godot-proposals#4958](https://github.com/godotengine/godot-proposals/issues/4958) (\`--script-dump-ast\`) — same pattern (cmdline → JSON to stdout → quit), different subject (scene tree instead of GDScript AST).

\`\`\`bash
godot --headless --path /my/project --inspect-scene res://main.tscn
\`\`\`

Loads a \`.tscn\` without launching the editor, walks the node tree, prints a single nested JSON object to stdout, exits. Each node has \`name\`, \`class\`, optional \`properties\` (editor-visible only), optional \`children\`. Useful for scripted scene analysis, CI checks, and (in our case) AI agents that need to read scene structure without a running editor.

Implementation: a new \`SceneInspector\` helper in \`core/io/scene_inspector.{h,cpp}\` and a hook early in \`Main::start()\`.

This commit also includes one drive-by macOS fix: the \"no main scene defined\" check used to fire a modal \`NSAlert\` on macOS even for cmdline tools that legitimately have no main scene. The guard now respects \`cmdline_tool\` so headless invocations don't hang waiting for a dismiss.

## Why both together

I considered splitting into two PRs but they share the same motivating use case (closing the loop for headless / scripted Godot workflows) and touch disjoint files (\`core/io/logger.{h,cpp}\` vs \`core/io/scene_inspector.{h,cpp}\`). Happy to split if reviewers prefer.

## Test plan

- \`scons platform=linuxbsd target=editor\` and \`platform=macos target=editor\` (verified locally on macOS arm64)
- \`godot --headless --log-format json --script test.gd\` — verify NDJSON output, one JSON object per line
- \`godot --headless --log-format json --script broken.gd\` — verify parse/compile errors emit structured records with \`file\`, \`line\`, \`code\`
- \`godot --headless --path proj --inspect-scene res://main.tscn\` — verify tree dump, exits cleanly
- Default invocations unchanged (regression check)

## COMMENTS
--- Ivorforce:
AI generated PR, violating our PR rules and ignoring the template.


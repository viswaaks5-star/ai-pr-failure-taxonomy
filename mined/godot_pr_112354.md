# PR 112354 [CLOSED] — Fix MSVC version parsing for Visual Studio in methods.py
AUTHOR: jvastola

## BODY
Description:
This PR updates the version parsing logic in methods.py to robustly extract only the numeric parts of the MSVC version string. This prevents a ValueError when building Godot with Visual Studio 2026 (Insiders) or newer, whose version strings include non-numeric text (e.g., "Insiders").

Details:

Uses regex to extract leading digits for major, minor, and patch version numbers.
Fixes build failure on new Visual Studio releases where the version string format changed.
Testing:

Verified that Godot now builds successfully with Visual Studio 2026 Developer Command Prompt.
Confirmed that the fix does not affect builds with previous Visual Studio versions.
Related issues:

Fixes build error: [ValueError: invalid literal for int() with base 10: ' Insiders [ValueError: invalid literal for int() with base 10: ' Insiders [11123'](vscode-file://vscode-app/c:/Users/Admin/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)

## COMMENTS
--- akien-mga:
This seems similar to #111918 but that PR seems to take a slightly more reliable approach, so I'll close this in favor of #111918.

Please note for future PRs that we don't want to use Copilot AI for reviews on the @godotengine organization.


# PR 118125 [CLOSED] — GDScript: Add code coverage instrumentation
AUTHOR: cristim

## BODY
## Summary

This PR adds line, function, and branch coverage instrumentation to the GDScript VM, with writers for four output formats (LCOV, Cobertura XML, JSON, plain text), command-line integration, and a comprehensive unit test suite.

Coverage is a `TOOLS_ENABLED`-only feature — the entire implementation compiles to nothing in release/export builds and has zero runtime overhead when disabled.

---

## How it works

### 1. Instrumentation — VM opcode hooks

Three opcode handlers in `gdscript_vm.cpp` are extended with recording hooks guarded by `unlikely()` so the branch predictor eliminates overhead when coverage is disabled:

| Opcode | What is recorded |
|---|---|
| `OPCODE_LINE` | Line hit — increments (or sets to 1 in *set* mode) the counter for that file/line |
| `OPCODE_JUMP_IF` | Branch outcome — records the boolean result of the condition |
| `OPCODE_JUMP_IF_NOT` | Branch outcome (inverted sense) |

Function entry is recorded once at the top of `GDScriptFunction::call()`. For scripts with inner classes, method names are qualified with the inner-class chain (e.g. `Outer.Inner.method_name`) so that same-named methods in different inner classes produce distinct keys.

The hot flag `coverage_enabled` is a `SafeFlag` (backed by `std::atomic<uint32_t>`) so reads from VM threads have acquire/release ordering without taking any lock.

### 2. Data storage — thread safety

All three hit maps are `HashMap`s owned by `GDScriptLanguage`:

```
coverage_hits:        file → line  → hit count
coverage_func_hits:   file → func  → hit count
coverage_branch_hits: file → ip    → {taken, not_taken, line}
```

A single `Mutex coverage_mutex` serialises writes from concurrent VM threads. The hot path in set mode:

```cpp
MutexLock lock(coverage_mutex);
coverage_hits[source][line] = 1;
```

Reads for output take a snapshot under the mutex and then work on the copy, so writers never hold the lock longer than a map copy.

### 3. Coverable-line enumeration

To report lines and functions that were *compiled but never executed*, the writers walk `GDScriptLanguage::script_list` and introspect bytecode via `GDScriptFunction::get_code()` — the same mechanism used by the debugger. Only scripts that were actually loaded/parsed during the session appear. Scripts that exist on disk but were never loaded cannot be reported.

Include/exclude glob patterns (`--coverage-include` / `--coverage-exclude`) are applied at enumeration time so all formats share a consistent view.

### 4. Output formats

| Flag value | Format | Consumed by |
|---|---|---|
| `lcov` (default) | LCOV `.info` | `genhtml`, `lcov`, `gcovr`, GitHub Actions coverage reporters |
| `cobertura` | Cobertura XML | Jenkins, GitLab CI, Azure DevOps, Codecov |
| `json` | Custom JSON | custom dashboards, diff tools |
| `text` | Human-readable summary | terminal / CI log |

All formats include unexecuted files (lines and functions at count 0) so percentages are accurate even for scripts that are compiled but never called during the test run.

### 5. Command-line integration

Arguments are parsed once in `GDScriptLanguage::init()`:

```
--coverage-output <path>       path to write the coverage file (enables coverage)
--coverage-format <fmt>        lcov | cobertura | json | text  (default: lcov)
--coverage-mode <mode>         set | count  (default: set)
--coverage-threshold <pct>     fail if line coverage is below this %
--coverage-include <glob>      include only matching files (repeatable)
--coverage-exclude <glob>      exclude matching files (repeatable)
```

`coverage_write()` is called automatically from:
- `GDScriptLanguage::finish()` — when the engine exits normally
- The GDScript test runner suite — after `runner.run_tests()` completes

If `--coverage-threshold` is set and line coverage falls below it, the engine prints an error and exits with a non-zero exit code.

---

## Example

Consider this project layout:

```
res://
  src/
    math.gd
  tests/
    test_math.gd
```

**`src/math.gd`**
```gdscript
func add(a, b):
    return a + b

func divide(a, b):
    if b == 0:
        return 0
    return a / b
```

**`tests/test_math.gd`**
```gdscript
extends SceneTree

func _init():
    var math = load("res://src/math.gd").new()

    assert(math.add(2, 3) == 5)
    assert(math.add(-1, 1) == 0)

    # Call divide() with a non-zero divisor only — the b==0 branch is uncovered
    assert(math.divide(10, 2) == 5)

    print("All tests passed.")
    quit()
```

Run with coverage:

```sh
godot --headless \
      --coverage-output coverage.info \
      --coverage-format lcov \
      --coverage-include "res://src/*" \
      -s tests/test_math.gd
```

**`coverage.info` (LCOV output)**

```
TN:
SF:/path/to/project/src/math.gd
FN:0,@implicit_new
FN:2,add
FN:5,divide
FNDA:1,@implicit_new
FNDA:1,add
FNDA:1,divide
FNF:3
FNH:3
BRDA:5,11,0,1
BRDA:5,11,1,0
BRF:2
BRH:1
DA:2,1
DA:5,1
DA:6,0
DA:7,1
LF:4
LH:3
end_of_record
```

- `FN:0,@implicit_new` — GDScript adds an implicit constructor for scripts without an explicit `_init()`; its start line is reported as 0 because it has no `OPCODE_LINE` opcode.
- `FN:2,add` and `FN:5,divide` — start lines are the first executable statement in each function.
- `BRDA:5,11,0,1` — the `if b == 0:` branch at line 5, instruction offset 11: the "condition true" arm was taken 1 time; the "condition false" arm (`BRDA:5,11,1,0`) was never taken because we only called `divide(10, 2)`.
- `DA:6,0` — `return 0` was never reached.

The same run produces this **Cobertura XML**:

```xml
<?xml version="1.0" ?>
<!DOCTYPE coverage SYSTEM "http://cobertura.sourceforge.net/xml/coverage-04.dtd">
<coverage version="5.0" timestamp="..." line-rate="0.7500" branch-rate="0.5000"
          lines-covered="3" lines-valid="4" branches-covered="1" branches-valid="2">
  <packages>
    <package name="gdscript" line-rate="0.7500" branch-rate="0.5000" complexity="0">
      <classes>
        <class name="math" filename="/path/to/project/src/math.gd"
               line-rate="0.7500" branch-rate="0.5000">
          <methods>
            <method name="@implicit_new" hits="1"/>
            <method name="add" hits="1"/>
            <method name="divide" hits="1"/>
          </methods>
          <lines>
            <line number="2" hits="1" branch="false"/>
            <line number="5" hits="1" branch="true" condition-coverage="50% (1/2)"/>
            <line number="6" hits="0" branch="false"/>
            <line number="7" hits="1" branch="false"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
```

And this **JSON**:

```json
{
  "files": {
    "res://src/math.gd": {
      "lines":     {"2": 1, "5": 1, "6": 0, "7": 1},
      "functions": {"@implicit_new": 1, "add": 1, "divide": 1},
      "branches":  {"11_taken": 1, "11_not_taken": 0}
    }
  },
  "summary": {"line_pct": 75.0, "func_pct": 100.0, "branch_pct": 50.0}
}
```

And this **text summary**:

```
File                                    Lines    Funcs    Branches
res://src/math.gd                       75.0%    100.0%   50.0%
────────────────────────────────────────────────────────────
Total                                   75.0%    100.0%   50.0%
```

**Using with the built-in GDScript test suite:**

```sh
godot --headless \
      --coverage-output coverage.info \
      --coverage-threshold 75 \
      -- --test --test-suite "[Modules][GDScript]"
```

**Uploading to Codecov from GitHub Actions:**

```yaml
- name: Run GDScript tests with coverage
  run: |
    godot --headless \
          --coverage-output coverage.info \
          --coverage-threshold 75 \
          -- --test --test-suite "[Modules][GDScript]"

- name: Upload coverage report
  uses: codecov/codecov-action@v4
  with:
    files: coverage.info
```

---

## Files changed

| File | Change |
|---|---|
| `modules/gdscript/gdscript.h` | Coverage data structures, enums, `SafeFlag coverage_enabled`, method declarations |
| `modules/gdscript/gdscript_coverage.cpp` | New file — all coverage logic: recording, coverable-line enumeration, four format writers |
| `modules/gdscript/gdscript_vm.cpp` | Opcode hooks for line, function, and branch recording |
| `modules/gdscript/gdscript.cpp` | CLI arg parsing; auto-start on `init()`; auto-write + threshold check on `finish()` |
| `modules/gdscript/tests/test_gdscript_coverage.h` | 35+ unit tests covering all recording paths and all four output formats |
| `modules/gdscript/tests/gdscript_test_runner_suite.h` | Wire `coverage_write()` return value check into the GDScript test runner |

## COMMENTS
--- clayjohn:
Sorry, we aren't accepting AI-generated PRs right now. 

For new features, we insist that contributors follow the proper procedure including opening a proposal in advance. We insist on this so we have a chance to gauge interest in the feature and have a chance to discuss performance/maintenance implications of the change. 

Also please note, your failure to disclose that this was vibe-coded is against our AI contribution policy https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions

--- cristim:
@clayjohn fair enough, I built it for myself as I was working on a project and thought this might be useful to the project.

Have a great day!


--- cristim:
@clayjohn to add a few more words to what I wrote earlier.

Most other main programming languages have such test coverage reporting functionality. I wanted to also see it in the Gogot scripting language, so I built it and shared it, thinking that people from the wider community will find it useful as well. 

Yes, this is clearly generated by AI, but based on thorough planning and carefully tested. Before submitting it I tried to refactor it to have great code quality and it passes all your pre-commit checks. (I'd rather describe it as vibe-engineered as opposed to vibe-coded).

I agree I didn't get to read your contribution guidelines, and that I should have raised this before as a feature request, but to be honest this was intentionally a drive-by contribution.

I don't plan to do more contributions to Godot anytime soon and don't feel like getting up to speed with all your development processes and policies.

If anyone out there also finds this feature useful enough to take it through the official process, that would be great, otherwise I really don't care, feel free to take it or leave it.


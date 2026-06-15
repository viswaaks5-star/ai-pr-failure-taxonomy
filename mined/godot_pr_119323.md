# PR 119323 [CLOSED] — Seed RandomPCG::randomize() from the OS cryptographic randomness source
AUTHOR: w4nderlust

## BODY
> [!INFO]
> **AI disclosure**: I investigated the bug, wrote the failing test that reproduces it, and implemented the fix myself. AI assistance was used for searching prior issues and PRs related to RNG seeding, light autocomplete and comment polish while coding, and reorganising this description for clarity. The debugging, solution design, and implementation are mine.

### What this fixes

`RandomPCG::randomize()` derives its seed from a microsecond-resolution clock. Constructing a `RandomNumberGenerator` takes well under a microsecond on modern hardware, so two `RandomNumberGenerator.new()` calls in the same frame routinely read the same timestamp, get the same seed, and emit identical streams. Since #66989 made the constructor auto-call `randomize()`, this affects every default-constructed instance.

Closes #119322. Re-addresses #48087, whose 2021 mitigation did not cover the dominant intra-second case.

### What changed

`RandomPCG::randomize()` now seeds from the OS CSPRNG: `BCryptGenRandom` on Windows, `getentropy` on Linux, macOS, iOS, BSDs, Android (API 28+), and Web via Emscripten. A SplitMix64-finalised counter and time mix is kept as a fallback for unrecognised builds, so back-to-back calls still receive distinct seeds even there. A regression test in `tests/core/math/test_random_number_generator.cpp` asserts no first-output collisions across 1000 consecutive constructions.

### Empirical validation

5000 trials, each constructing a fresh `RandomNumberGenerator` and rolling 5d6. Expected ties for a fair RNG: ~0.64.

| Variant                          | Identical consecutive 5d6 |
| -------------------------------- | ------------------------: |
| Before, fresh per trial          | 2168                      |
| After, fresh per trial           | 0                         |
| Reused single instance (control) | 1                         |

Independent verification at N=100,000,000 on a release build (Windows, fresh hardware): 57,287,074 ties out of 99,999,999 before the patch (expected ~12,860, roughly 4,455x over). The size of the gap depends on per-iteration time relative to one microsecond, which is the entropy resolution of the current formula.

### Cost

Approximately 200 to 800 ns per `randomize()` call. End-to-end cost of `RandomNumberGenerator.new()` plus reading `seed` measures around 300 to 400 ns on modern hardware (M-series Mac and a fast Windows desktop) in Godot 4.6.2 release headless builds. No measurable frame-time impact.

### Backwards compatibility

Deterministic seeding via `seed(N)` / `set_seed(N)` is unchanged. Only the implicit seed value picked by `randomize()` changes. `Math::default_rand` is untouched.


## COMMENTS
--- Ivorforce:
Hello, did you use AI to generate either code and/or the PR description?

--- w4nderlust:
> Hello, did you use AI to generate either code and/or the PR description?

Yep. I investigated the issue myself, wrote the failing test that reproduces it, and implemented the fix. I also used AI tooling during the process in a few supporting ways:

* to search for existing issues/PRs related to the bug
* for some autocomplete/comment assistance while coding
* to help reorganize and polish the final issue/PR description for clarity and references

The actual debugging, solution design, and implementation work were mine, but AI-assisted tooling was part of the workflow.

--- issork:
To add to my review - I don't see the point of this PR. Generating multiple RNGs that guarantee a different seed in a loop can be easily achieved by populating the RNGs seeds with the output of a single extra RNG.

--- w4nderlust:
> To add to my review - I don't see the point of this PR. Generating multiple RNGs that guarantee a different seed in a loop can be easily achieved by populating the RNGs seeds with the output of a single extra RNG.

That works as a workaround, but it's basically asking every user to manually do in script what the engine could do once internally. It also still requires you to know about the bug to apply the pattern, and it doesn't match what the docs already say about fresh instances being independent. The "point of this PR" is that the fix lives in the engine instead of in every user's project.

--- AThousandShips:
Please reduce the verbosity of your PR description, there's no reason to repeat the changes from the PR in the description, and this is extremely hard to read and get any useful details from

--- Ivorforce:
> > Hello, did you use AI to generate either code and/or the PR description?
> 
> Yep. I investigated the issue myself, wrote the failing test that reproduces it, and implemented the fix. I also used AI tooling during the process in a few supporting ways:
> 
> * to search for existing issues/PRs related to the bug
> * for some autocomplete/comment assistance while coding
> * to help reorganize and polish the final issue/PR description for clarity and references
> 
> The actual debugging, solution design, and implementation work were mine, but AI-assisted tooling was part of the workflow.

Please amend your PR description with a well-visible AI disclaimer describing what exactly you used it for. Using AI to write code and not disclosing it violates our [PR rules](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions); on repeated offense you might be banned from contributing to the project. Submitting a huge PR/description and not even bothering to read our 5-sentence checklist for new contributors is also a bad first impression.

--- w4nderlust:
> Paying more attention to your text now. You wrote about get_ticks_usec() having microsecond resolution, while it is in fact nanoseconds.
> 
> Also your own test appears to be accurate, so I don't think this is indeed an issue at all? For n = 100000000, I got the following result:
> 
> ```
> Identical consecutive 5d6 sequences: 12802 / 99999999
> Expected for a fair RNG: ~12860.08
> ```
> 
> Which is, I believe, within an acceptable margin of randomness.

Thanks for running it. The result is very hardware/build dependent: on a fresh Windows desktop in a release build I just ran the same N=100,000,000 and got 57,287,074 ties out of 99,999,999 (expected ~12,860, ratio ~4,455x), with a per-iteration time of 428 ns. The bug triggers when iteration time falls under one microsecond, which it does on most modern desktops in a release build. Your 12,802 result means your per-iteration time was over a microsecond on your machine, which puts each construction in a different timestamp bucket and hides the bug. The issue isn't "no bug, everywhere" or "bug, everywhere", it's "bug, on machines fast enough to construct an RNG in under a microsecond", which is most of them these days.

--- w4nderlust:
> Please reduce the verbosity of your PR description, there's no reason to repeat the changes from the PR in the description, and this is extremely hard to read and get any useful details from

> Please amend your PR description with a well-visible AI disclaimer describing what exactly you used it for. Using AI to write code and not disclosing it violates our [PR rules](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions); on repeated offense you might be banned from contributing to the project. Submitting a huge PR/description and not even bothering to read our 5-sentence checklist for new contributors is also a bad first impression.

Updated, shortened, and added the disclaimer.


--- AThousandShips:
This seems to me like a limitation to document and provide suggestions for, not something requiring a lot of platform dependent code to do universally, what benefit does it serve outside this specific rare use case?

--- w4nderlust:
> This seems to me like a limitation to document and provide suggestions for, not something requiring a lot of platform dependent code to do universally, what benefit does it serve outside this specific rare use case?

Imho a code fix is worth more here than a doc note:

Per-instance RNGs aren't a rare pattern: encapsulated systems that own their own state (cards, units, agents), multi-threaded code where each job wants its own stream, per-chunk procedural generators, test fixtures, and addons that can't enforce engine-wide patterns on user code. The recurring history of this report (#48087 in 2021, broadened by #66989, fresh report now) suggests it bites people more often than the tracker implies.

A doc warning only helps users who read it. A code fix helps all of them, including future users and plugin authors, and matches what the class reference already says ("multiple instances, each with their own seed and state") instead of adding a footnote that contradicts it.

On "a lot of platform code": it's one helper with a `#ifdef` branch per OS family and two standard API calls (`getentropy` on Unix-likes including Web, `BCryptGenRandom` on Windows). A fallback covers unrecognised builds so nothing breaks.

--- AThousandShips:
> On "a lot of platform code": it's one helper with a `#ifdef` branch per OS family and two standard API calls (`getentropy` on Unix-likes including Web, `BCryptGenRandom` on Windows)

That's what I mean with platform code, it naturally has to be `#ifdef`d, adding platform specific code outside `platform/` should be avoided

I'd say that initializing a lot of random generators in individual objects and having them initialize at the same time (i.e. in microsecond precision) is not a common pattern, and making the code in question more fragile, especially when it can be worked around with a few lines of code, it also makes it dependent on the cryptographic random system which can have unpredictable speed in generation depending on the entropy available, generating many RNGs at the same time can potentially be slow, i.e. the specific use case, it would also add a cost every time an RNG is created and then immediately re-seeded

Additionally a lot of randomness in various kinds of projects seed their randomness on per-instance basis with a global source if they are seeded with configuration

I'm not convinced the entire use case for this isn't a code smell, but even if it isn't it is trivially solvable without affecting all randomness use

--- w4nderlust:
> > On "a lot of platform code": it's one helper with a `#ifdef` branch per OS family and two standard API calls (`getentropy` on Unix-likes including Web, `BCryptGenRandom` on Windows)
> 
> That's what I mean with platform code, it naturally has to be `#ifdef`d, adding platform specific code outside `platform/` should be avoided
> 
> I'd say that initializing a lot of random generators in individual objects and having them initialize at the same time (i.e. in microsecond precision) is not a common pattern, and making the code in question more fragile, especially when it can be worked around with a few lines of code, it also makes it dependent on the cryptographic random system which can have unpredictable speed in generation depending on the entropy available, generating many RNGs at the same time can potentially be slow, i.e. the specific use case, it would also add a cost every time an RNG is created and then immediately re-seeded
> 
> Additionally a lot of randomness in various kinds of projects seed their randomness on per-instance basis with a global source if they are seeded with configuration
> 
> I'm not convinced the entire use case for this isn't a code smell, but even if it isn't it is trivially solvable without affecting all randomness use

Fair on the platform code organization. The right move is to lift the helper out of `random_pcg.cpp` and into `OS::get_entropy()` (or similar) on the singleton, with the platform branches living in `platform/windows/os_windows.cpp`, `drivers/unix/os_unix.cpp`, and the Web override. `random_pcg.cpp` then just calls `OS::get_singleton()->get_entropy(...)` with no `#ifdef`. If that's your preference I'm happy to refactor accordingly.

On whether the use case warrants the change at all, the comparative landscape is informative and .NET is the closest precedent. Before .NET 6, `new Random()` was seeded from `Environment.TickCount`, which is the same mechanism Godot uses today and produces the same intra-quantum collision. Microsoft moved away from that in [dotnet/runtime#47085](https://github.com/dotnet/runtime/pull/47085) (merged Jan 2021), which states the motivation explicitly:

> "sometimes trying to workaround the poor default seed quality we had in .NET Framework, where the seed was based on Environment.TickCount and thus lots of Randoms created in the same quantum would end up with the same seed"

Python (`os.urandom`), Java (`AtomicLong` uniquifier mixed with `nanoTime`), Rust (`getrandom` via the de facto `rand` crate), and idiomatic C++ (`std::random_device`) all sit on the same side. Each of those teams independently concluded that quietly returning correlated streams from default-constructed instances was worth a small per-construction cost to fix. This PR aligns Godot with that direction.

--- AThousandShips:
Also per the new performance measurements this means the initialization is between 2/3rds slower to twice as slow, that's not a negligible cost for something that won't matter for the overwhelming use cases of this

--- w4nderlust:
> Also per the new performance measurements this means the initialization is between 2/3rds slower to twice as slow, that's not a negligible cost for something that won't matter for the overwhelming use cases of this

Math is right, ~60% to 2x slower in relative terms on the construction path. In absolute terms it's 200 to 800 ns once per `randomize()` call. For the intended pattern of "create one RNG and reuse it for the lifetime of the system", that's a single added syscall at init time, traded for the seed actually being independent. Hard to call that not worth it.

If the relative cost on the per-construction path is still the blocker, the middle ground is what .NET 6 did in [dotnet/runtime#47085](https://github.com/dotnet/runtime/pull/47085): seed a thread-local mixer from the OS once, then derive each `randomize()` seed from that mixer. One kernel call per thread instead of one per construction, same correctness properties, ~10 to 50 ns per construction. Happy to refactor the PR to that shape if maintainers prefer the lower amortised cost.

--- AThousandShips:
My issue with this is that there's a repeated refusal to consider the fact that this doesn't help the vast majority of cases, and that the "issue" this solves is extremely unlikely to happen to the general user, while adding complexity and cost to the calls for everyone, regardless of the need for it

This attitude to engine improvement is not something I can get behind, it shows a very skewed approach to considering the pro/con situation for engine changes, dismissing the cost and impact (including maintenance cost) and magnifying the issue

--- w4nderlust:
> If we do this at all, and I'm not sure we should, obviously the actual implementation of getting the seed needs to live in os, with per platform implementations in platform/
> 
> But in this form this can't be merged

Done, it's actually nicer thanks to your suggestion, reduced code by 63 lines.

--- w4nderlust:
> My issue with this is that there's a repeated refusal to consider the fact that this doesn't help the vast majority of cases, and that the "issue" this solves is extremely unlikely to happen to the general user, while adding complexity and cost to the calls for everyone, regardless of the need for it
> 
> This attitude to engine improvement is not something I can get behind, it shows a very skewed approach to considering the pro/con situation for engine changes, dismissing the cost and impact (including maintenance cost) and magnifying the issue

Respectfully, I don't think the framing is quite right. The use case is clearly less niche than "extremely unlikely": this is the third time the same bug has surfaced on the tracker (#48087 in 2021, #66989 broadened it in 2022, this one now), and almost every other modern stdlib has independently concluded it was worth fixing the same way this PR does (Python from `os.urandom`, Java's `AtomicLong` uniquifier, .NET 6's thread-local OS-seeded mixer in dotnet/runtime#47085, Rust's `getrandom`, modern C++'s `std::random_device`). That's a lot of independent groups making the same call. Worth weighing as evidence rather than dismissing.

I'm not dismissing the cost either. We've had an honest exchange of measurements: ~100 lines of (now mostly self-contained) code, one syscall per `randomize()` call, ~200 to 800 ns added once per long-lived RNG (or per construction if you create them per-instance, which is the case the PR actually fixes). I think correctness wins that trade in my opinion, but it's a judgment call and I'm fine being on the losing side of it if the team disagrees.

If "won't merge" is the answer after considering the current diff (which is a net `-63` lines and uses the existing `OS::get_entropy()` infrastructure rather than adding platform branches in core), that's your call to make and I'll respect it. Just wanted the position to be evaluated on the actual numbers rather than on a stronger version of the disagreement than I'm holding.

--- AThousandShips:
There have been two reports, one of which was yours, https://github.com/godotengine/godot/issues/66989 had nothing to do with this, this is very dishonest in the framing TBH

"Correctness" here is very specific, the current implementation isn't incorrect

But this is clearly not going anywhere, so I won't continue the conversation, but hopefully that'll cast some light on it for other reviewers, that this should be documented, speaking as a documentation maintainer

--- w4nderlust:
> There have been two reports, one of which was yours, #66989 had nothing to do with this, this is very dishonest in the framing TBH
> 
> "Correctness" here is very specific, the current implementation isn't incorrect
> 
> But this is clearly not going anywhere, so I won't continue the conversation, but hopefully that'll cast some light on it for other reviewers, that this should be documented, speaking as a documentation maintainer

Honestly, I'm tired of this conversation. To be clear: I'm not generating these comments with AI, I disclosed my use of AI assistance upfront and added it to the PR when asked, exactly as the contributing guidelines ask. Treating thorough citations and structured replies as evidence of dishonesty isn't a productive frame for either of us, and I feel disrespected.

I've made every technical change you asked for: shortened the description, added the AI disclosure, switched the test to assert on `seed` directly, corrected the inaccurate "1 to 5 us" line with the real measured number, refactored the platform code out of `core/math` into the existing `OS::get_entropy()` infrastructure (net `-63` lines, no new platform branches anywhere), and switched `std::atomic` for `SafeNumeric`. The current diff is well researched, well tested, and aligned with what every other major language standard library does for the same reason.

I'm happy to make further changes if other maintainers see room for improvement. I won't keep relitigating the design judgment, the team can land where it lands, and I'll respect the call. But the substance of the PR is the substance, and I'd ask that it be evaluated on that rather than on a read of how I'm communicating.

--- w4nderlust:
> Very verbose AI generated comments.

Trimmed them down as requested.

--- hpvb:
AI generated comments in the PR, lying about AI use, unclear benefits.

--- w4nderlust:
> AI generated comments in the PR, lying about AI use, unclear benefits.

What lying are you talking about? I guess you prefer keeping it broken over fixing something for your users, more power to you I guess.

Honestly, I contribute to open source projects and run them for the last 15 years of my life. I've never felt so disrespected by maintainers ever. And for what? For fixing a bug i ntheir code. Wow.

--- hpvb:
Are you really going to sit here with a straight face and claim you wrote this with your own meat fingers on a keyboard? Because this is EXACTLY what I'd expect Claude to write. 

> I'm happy to make further changes if other maintainers see room for improvement. I won't keep relitigating the design judgment, the team can land where it lands, and I'll respect the call. But the substance of the PR is the substance, and I'd ask that it be evaluated on that rather than on a read of how I'm communicating.

If you want to contribute to the engine that would be great, but please don't treat us like idiots okay?

--- w4nderlust:
> Are you really going to sit here with a straight face and claim you wrote this with your own meat fingers on a keyboard? Because this is EXACTLY what I'd expect Claude to write.
> 
> > I'm happy to make further changes if other maintainers see room for improvement. I won't keep relitigating the design judgment, the team can land where it lands, and I'll respect the call. But the substance of the PR is the substance, and I'd ask that it be evaluated on that rather than on a read of how I'm communicating.
> 
> If you want to contribute to the engine that would be great, but please don't treat us like idiots okay?

You are the ones who have been treating me like an idiot. yes I wrote all of that myself with my meat fingers, was trying to be polite and helpful. I just got witchhunted in return. You should stop treating contributors in a disrespectful and toxic way if you truly want people to contribute.


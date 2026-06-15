# PR 117314 [CLOSED] — core/templates: add SPSCRing<T,SIZE> lock-free SPSC ring buffer
AUTHOR: Mattbusel

## BODY
## What this adds

`core/templates/spsc_ring.h` — a `SPSCRing<T, SIZE>` template: a lock-free, zero-allocation ring buffer safe for exactly one producer thread and one consumer thread.

## Why this is needed

The existing `RingBuffer<T>` (`core/templates/ring_buffer.h`) uses plain `int` indices with no synchronisation and is explicitly single-threaded. It cannot be safely used across threads.

The audio system works around this today with `AudioRBResampler`, which reimplements the SPSC pattern manually using `SafeNumeric<int>` — but that primitive is private to the resampler and cannot be reused.

`SPSCRing` gives Godot a clean, reusable, formally correct SPSC primitive for any two-thread pipeline: audio command queues, network receive → decode, physics event feeds, etc.

## Properties

| Property | Detail |
|---|---|
| Lock-free | No `Mutex`, `BinaryMutex`, `Semaphore`, or spin-lock |
| Zero heap allocation | Storage is a fixed inline `std::array` — `SIZE*sizeof(T) + 128` bytes total |
| Cache-friendly | `tail_` and `head_` on separate `alignas(64)` cache lines, eliminating false sharing between producer and consumer |
| noexcept | `push`/`pop` never throw provided T satisfies noexcept move requirements |
| Non-blocking | `push()` returns `false` when full; `pop()` returns `false` and leaves the output unchanged when empty |
| MSVC-compatible | C4324 (intentional alignment padding) explicitly suppressed |
| Compile-time asserts | SIZE power-of-two in [2, 2^30]; T noexcept move-constructible/assignable |

## Interface

```cpp
// Shared between two threads:
SPSCRing<AudioCommand, 1024> commands;

// Main thread (producer):
AudioCommand cmd = make_command(...);
if (!commands.push(std::move(cmd))) {
    // ring full — drop or handle backpressure
}

// Audio thread (consumer):
AudioCommand out;
while (commands.pop(out)) {
    execute(out);
}
```

```cpp
static constexpr size_t capacity();   // SIZE - 1 usable slots

bool push(T&&);                        // producer thread only
bool push(const T&);                   // copy convenience overload
bool pop(T& out);                      // consumer thread only; false = empty

size_t size_approx() const;            // monitoring only (non-atomic)
bool   empty_approx() const;
bool   full_approx()  const;
```

## Files changed

- `core/templates/spsc_ring.h` — new file (168 lines including MIT header, full doc comments, static_asserts)

Designed and implemented by Matthew Busel.

## COMMENTS
--- arkology:
> —


> Designed and implemented by Matthew Busel.

I have serious doubts about it. Especially after looking at the profile info (filled with bunch of LLM stuff).

--- AThousandShips:
Closing as this is not a demanded feature, that is not used anywhere, and the above comment, please open a proposal if you have a good argument for adding this feature, and present actual use cases in the engine

Thank you for your contribution nonetheless 

--- akien-mga:
Checked the user profile briefly and the first PR I look at shows signs of being abusive towards maintainers: https://github.com/rust-unofficial/awesome-rust/pull/2264#issuecomment-4017399259

So blocking them preemptively. We have no tolerance for AI slop.


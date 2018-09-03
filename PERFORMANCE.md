## array instead of list

array, bytearray, bytes

```
ba = bytearray(10000)  # big array
func(ba[30:2000])      # a copy is passed, ~2K new allocation
mv = memoryview(ba)    # small object is allocated
func(mv[30:2000])      # a pointer to memory is passed
```

## Avoid floating point

floats allocate RAM!

time.sleep(0.1) -> time.sleep_ms(100)

integer division where possible: 9/2 -> 9//2

## readinto() instead of read()

readinto() an already allocated array

## Hardware random

random.randint(10) -> machine.random(10)

## Allocate bound vars to local scope

```
class Foo:
    def foo():
        bar = self.bar
        (...)
```

## Use const() declaration

This works in a similar way to #define in C in that when the code is compiled to bytecode the compiler substitutes the numeric value for the identifier. This avoids a dictionary lookup at runtime. The argument to const() may be anything which, at compile time, evaluates to an integer e.g. 0x100 or 1 << 8.

s

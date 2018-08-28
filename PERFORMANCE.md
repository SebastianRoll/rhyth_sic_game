## array instead of list

array, bytearray, bytes

## Avoid floating point

floats allocate RAM!

time.sleep(0.1) -> time.sleep_ms(100)

9/2 -> 9//2

## readinto() instead of read()

readinto() an already allocated array

## Hardware random

random.randint(10) -> machine.random(10)

## Allocate bound vars to local scope

```
def foo():
    bar = self.bar
    (...)
```


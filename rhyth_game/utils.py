import utime
import machine
import gc


def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))

        # if delta > 30000:
            # print(free(full=True))
            # print(*args, **kwargs)
            # print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
            # raise Exception('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func


def free(full=False):
  # gc.collect()
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}%'.format(F/T*100)
  if not full: return P
  else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))


def reset():
    machine.reset()

# @micropython.asm_thumb
# def byteswap(r0, r1):               # bytearray, len(bytearray)
#     cmp(r1, 1)
#     ble(FAIL)
#     mov(r3, 1)
#     lsr(r1, r3) # divide len by 2
#     mov(r4, r0)
#     add(r4, 1) # dest address
#     label(LOOP)
#     ldrb(r5, [r0, 0])
#     ldrb(r6, [r4, 0])
#     strb(r6, [r0, 0])
#     strb(r5, [r4, 0])
#     add(r0, 2)
#     add(r4, 2)
#     sub(r1, 1)
#     bne(LOOP)
#     mov(r0, 1)
#     b(END)
#     label(FAIL)
#     mov(r0, 0)
#     label(END)
#

# class MemoryViewRev(memoryview):
#     def __init__(self, reversed=False, *args, **kwargs):
#         super.__init__(*args, **kwargs)
#         self.reversed = reversed
#         self.mv_length = len(self)
#
#     def __getitem__(self, item):
#         return super().__getitem__(self.mv_length-item)
#
#     def __setitem__(self, pos, item):
#         super().__setitem__(self.mv_length-pos, item)
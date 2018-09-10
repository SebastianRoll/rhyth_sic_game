import utime
import machine

def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func


def reset():
    machine.reset()
#
# try:
#     import uasyncio as asyncio
# except ImportError:
#     import asyncio
# async def sleep_ms(duration):
#     try:
#         await asyncio.sleep_ms(duration)
#     except AttributeError:
#         await asyncio.sleep(duration/1000)

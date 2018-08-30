import gc

import neopixel
import uasyncio as asyncio
import random



class NeopixelSlice:
    def __init__(self, np: neopixel, pixels, lock=None):
        self.np = np
        self.pixels = pixels
        self.lock = lock

    def __setitem__(self, index, val):
        self.np.__setitem__(self.pixels[index], val)

    def __getitem__(self, index):
        return self.np.__getitem__(self.pixels[index])

    def write(self):
        self.np.write()

    async def fill(self, color):
        for i in range(len(self.pixels)):
            self[i] = color

    async def pulse(self):
        c = [0, 0, 0, 0]
        c[random.randint(0, 2)] = 255

        for i in range(len(self.pixels)):
            self[i] = c
            if i > 0:
               self[i-1] = (0, 0, 0)
            await asyncio.sleep_ms(20)
        self.np[self.pixels[-1]] = (0,0,0)

    @property
    def n(self):
        return len(self.pixels)


class OuterRing(NeopixelSlice):
    global_color = [0, 0, 0, 0]

    async def global_color_change(self):
        incr = 4
        while True:
            ic = random.randint(0, 2)
            self.global_color[ic] += incr
            await asyncio.sleep_ms(20)
            if self.global_color[ic] >= 255:
                incr = -4
            else:
                incr = 4

    async def transition_circle(self, degree=0):
        while True:
            for i in range(self.pixels):
                if not degree:
                    a = i
                else:
                    a = (i + 54) % 109
                self.np[a] = self.global_color
                await asyncio.sleep_ms(0)

    def from_degrees(self, degree):
        return int(degree*len(self.pixels)/360)

    def to_degrees(self, index):
        return int(360*index/len(self.pixels))


async def pulse(np, lock, invert=False):
    if invert:
        for idx in range(34,67,-1):
            await lock.acquire()
            np[idx] = (255, 0, 0)
            if idx > 0:
                np[idx - 1] = (0, 0, 0)
            lock.release()

            await asyncio.sleep_ms(10)
        np[34] = (0, 0, 0)
    else:
        for idx in range(34):
            await lock.acquire()
            np[idx] = (255,0,0)
            if idx > 0:
                np[idx-1] = (0,0,0)
            lock.release()

            await asyncio.sleep_ms(10)
        np[-1] = (0,0,0)


async def refresh_leds(np, lock, rate_ms=60):
    while True:
        await lock.acquire()
        np.write()
        lock.release()
        # gc.collect()
        # gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        await asyncio.sleep_ms(rate_ms)

async def refresh_leds_2(np, led_array, lock, rate_ms=60):
    while True:
        await lock.acquire()
        np.buf = led_array
        np.write()
        lock.release()
        # gc.collect()
        # gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        await asyncio.sleep_ms(rate_ms)


async def pulse_if_event(np, event):
    while True:
        print("awaiting event")
        await event
        print("FOUND event")
        #loop.create_task(np.pulse())
        await np.pulse()
        await pulse_circle(np, [1,2,3,4,5])
        event.clear()


async def pulse_circle(np, pixels):
    c = [0,0,0,0]
    c[random.randint(0,2)] = 255
    for i in pixels:
        np[i] = (0,200,0,0)
    await asyncio.sleep_ms(400)
    for i in pixels:
        np[i] = (0,0,0,0)
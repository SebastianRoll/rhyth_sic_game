import random
import utils
from array import array
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import math


async def simple(np):
    for i in range(np.n):
        np[i] = (0,30,0,0)
        np.write()
    np.fill((0,0,0,0))


async def simple2(np):
    while True:
        for i in range(np.n):
            np[i] = (0,30,0,0)
            await asyncio.sleep_ms(0)
        np.fill((0,0,0,0))



async def cylon_bounce(np, color, eye_size=2, speed_delay=30, return_delay=100):
    async def move_eye(i):
        np.fill((0, 0, 0, 0))
        color_fade = [c // 10 for c in color]
        np[i] = color_fade
        for j in range(1, eye_size + 1):
            np[i + j] = color
        np[i + eye_size + 1] = color_fade
        await asyncio.sleep_ms(speed_delay)

    while True:
        for i in range(np.n - eye_size - 2):
            await move_eye(i)

        if return_delay:
            await asyncio.sleep_ms(return_delay)
            for i in range(np.n - eye_size - 2, 0, -1):
                await move_eye(i)
            await asyncio.sleep_ms(return_delay)


async def running_lights(np, color, wave_delay=100):
    position = 0
    num_leds = np.n
    for j in range(num_leds* 2):
        position += 1
        for i in range(num_leds):
            # sine wave, 3 offset waves make a rainbow!
            # float level = sin(i+Position) * 127 + 128;
            # setPixel(i,level,0,0);
            # float level = sin(i+Position) * 127 + 128;
            # TODO: sin() hashmap!
            expr = (math.sin(i + position) * 127 + 128) / 255
            np[i] = [int(expr * c) for c in color]

        await asyncio.sleep_ms(wave_delay)


async def rainbow_cycle(np, speed_delay=100):
    leds_count = np.n
    c = bytearray(3)
    while True:
        for j in range(0, 256*5, 1):
            for i in range(leds_count):
                wheel(c, ((i*256//leds_count)+j) & 255)
                np[i] = c
            await asyncio.sleep_ms(speed_delay)


def wheel(c, wheel_pos):

    if wheel_pos < 85:
        c[0] = wheel_pos * 3
        c[1] = 255 - wheel_pos * 3
        c[2] = 0
    elif (wheel_pos < 170):
        wheel_pos -= 85
        c[0] = 255 - wheel_pos * 3
        c[1] = 0
        c[2] = wheel_pos * 3
    else:
        wheel_pos -= 170
        c[0] = 0
        c[1] = wheel_pos * 3
        c[2] = 255 - wheel_pos * 3
    return c



def setPixelHeatColor(np, idx, temperature, val):
    # Scale 'heat' down from 0-255 to 0-191
    t192 = temperature*191//255

    # calculate ramp up from
    heatramp = t192 & 63
    heatramp <<= 2

    if t192 > 128:
        val[0] = 255
        val[1] = 255
        val[2] = heatramp
    elif t192 > 64:
        val[0] = 255
        val[1] = heatramp
        val[2] = 0
    else:
        val[0] = heatramp
        val[1] = 0
        val[2] = 0
    np[idx*3] = val[0]
    np[idx*3+1] = val[1]
    np[idx*3+2] = val[2]


async def fire(np, cooling=50, sparking=120, speed_delay=20):
    # heat = bytearray(np.n)
    heat = bytearray(len(np)//3)
    val = bytearray(3)
    # num_leds = np.n
    num_leds = len(np)//3
    while True:
        fire_once(np, heat, val, num_leds, cooling, sparking)
        await asyncio.sleep_ms(speed_delay)

from utils import timed_function

@timed_function
def fire_once(np, heat, val, num_leds, cooling=50, sparking=120):
    # Step 1.  Cool down every cell a little

    max_num_cooling = (((cooling*10)//num_leds)+2)
    for i in range(num_leds):
        cooldown = random.randint(0, max_num_cooling)

        if cooldown>=heat[i]:
            heat[i] = 0
        else:
            heat[i] = heat[i] - cooldown

    # Step 2.  Heat from each cell drifts 'up' and diffuses a little
    for k in range(num_leds-1, 2, -1):
        heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) // 3

    # Step 3.  Randomly ignite new 'sparks' near the bottom
    if random.randint(0,255) < sparking:
        y = random.randint(0,7)
        heat[y] = heat[y] + random.randint(160, 255)

    # Step 4.  Convert heat to LED colors
    for j in range(num_leds):
        setPixelHeatColor(np, j, heat[j], val)



def fade_to_black(np, idx, fade_value):
    old_color = np[idx]
    new_color = [c-(c*fade_value//256) if c>10 else 0 for c in old_color]
    np[idx] = new_color


async def meteor(np, color, meteor_size=5, meteor_trail_decay=64, meteor_random_decay=True, speed_delay=50):
    black = bytearray(3)
    np.fill(black)
    num_leds = np.n
    for i in range(num_leds*2):
        # fade brightness all LEDs one step
        for j in range(num_leds):
            if not meteor_random_decay or random.randint(0,10)>5:
                fade_to_black(np, j, meteor_trail_decay)

        # draw meteor
        for j in range(meteor_size):
            if i-j < num_leds:
                np[i-j] = color

        await asyncio.sleep_ms(speed_delay)



class NeopixelMock:
    def __init__(self, size):
        self.n = size

    def __setitem__(self, index, val):
        print(index, val)

    def __getitem__(self, index):
        return [0, 0, 0]

    def fill(self, color):
        pass


if __name__ == "__main__":
    np = NeopixelMock(size=20)
    loop = asyncio.get_event_loop()
    # loop.create_task(cylon_bounce(np, [10], 2))
    loop.create_task(running_lights(np, [10, 1,0]))
    loop.run_forever()


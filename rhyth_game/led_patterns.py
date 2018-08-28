import random

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



async def cylon_bounce(np, color, eye_size=2, speed_delay=0.03, return_delay=0.100):
    async def move_eye(i):
        np.fill((0, 0, 0, 0))
        color_fade = [int(c / 10) for c in color]
        np[i] = color_fade
        for j in range(1, eye_size + 1):
            np[i + j] = color
        np[i + eye_size + 1] = color_fade
        await asyncio.sleep(speed_delay)

    for i in range(np.n - eye_size - 2):
        await move_eye(i)

    if return_delay:
        await asyncio.sleep(return_delay)
        for i in range(np.n - eye_size - 2, 0, -1):
            await move_eye(i)
        await asyncio.sleep(return_delay)


async def running_lights(np, color, wave_delay=0.1):
    position = 0

    for j in range(np.n * 2):
        position += 1
        for i in range(np.n):
            # sine wave, 3 offset waves make a rainbow!
            # float level = sin(i+Position) * 127 + 128;
            # setPixel(i,level,0,0);
            # float level = sin(i+Position) * 127 + 128;
            np[i] = [int(((math.sin(i + position) * 127 + 128) / 255) * c) for c in color]

        await asyncio.sleep(wave_delay)


async def rainbow_cycle(np, speed_delay=0.1):
    while True:
        for j in range(0, 256*5, 30):
            for i in range(np.n):
                c = wheel(int(((i*256/np.n)+j)) & 255)
                np[i] = c
            await asyncio.sleep(speed_delay)


def wheel(wheel_pos):
    c = [0,0,0]
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

def setPixelHeatColor(np, idx, temperature):
    # Scale 'heat' down from 0-255 to 0-191
    t192 = round(temperature*191/255)

    # calculate ramp up from
    heatramp = int(t192 / 3)
    heatramp = min(255, heatramp*4)

    # byte heatramp = t192 & 0x3F; // 0..63
    # heatramp <<= 2; // scale up to 0..252

    if t192 > 150:
        np[idx] = (255, 128, int(((t192-130)/61)*255))
    elif t192 > 75:
        np[idx] = (255, int(((t192-75)/75)*127), 0)
    else:
        np[idx] = (heatramp, 0, 0)
    #
    # # calculate ramp up from
    # heatramp = t192 & b'0x3F'
    # heatramp <<= 2
    # # byte heatramp = t192 & 0x3F; // 0..63
    # # heatramp <<= 2; // scale up to 0..252
    #
    # if t192 > b'0x80':
    #     np[idx] = (255, 255, heatramp)
    # elif t192 > b'0x40':
    #     np[idx] = (255, heatramp, 0)
    # else:
    #     np[idx] = (heatramp, 0, 0)



async def fire(np, cooling=50, sparking=120, speed_delay=0.010):
    heat = bytearray(np.n)
    while True:

        # Step 1.  Cool down every cell a little
        for i in range(np.n):
            cooldown = random.randint(0, int((((cooling*10)/np.n)+2)))

            if cooldown>=heat[i]:
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown

        # Step 2.  Heat from each cell drifts 'up' and diffuses a little
        for k in range(np.n-1, 2, -1):
            heat[k] = int((heat[k - 1] + heat[k - 2] + heat[k - 2]) / 3)

        # Step 3.  Randomly ignite new 'sparks' near the bottom
        if random.randint(0,255) < sparking:
            y = random.randint(0,7)
            heat[y] = heat[y] + random.randint(160, 255)

        # Step 4.  Convert heat to LED colors
        for j in range(np.n):
            setPixelHeatColor(np, j, heat[j])

        # np.write()
        await asyncio.sleep(speed_delay)


def fade_to_black(np, idx, fade_value):
    old_color = np[idx]
    new_color = list((int(c-(c*fade_value/256)) if c>10 else 0 for c in old_color))
    np[idx] = new_color


async def meteor(np, color=[100,200,50], meteor_size=5, meteor_trail_decay=64, meteor_random_decay=True, speed_delay=0.05):
    np.fill((0,0,0))
    for i in range(np.n*2):
        # fade brightness all LEDs one step
        for j in range(np.n):
            if not meteor_random_decay or random.randint(0,10)>5:
                fade_to_black(np, j, meteor_trail_decay)

        # draw meteor
        for j in range(meteor_size):
            if i-j < np.n:
                np[i-j] = color

        await asyncio.sleep(speed_delay)



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


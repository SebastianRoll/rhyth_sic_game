import random

try:
    import ustruct as struct
except ImportError:
    import struct
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

async def sleep_ms(duration):
    try:
        await asyncio.sleep_ms(duration)
    except AttributeError:
        await asyncio.sleep(duration/1000)

class Fire:
    def __init__(self, np, cooling=50, sparking=120, speed_delay=20):
        self.np = np
        self.cooling = cooling
        self.sparking = sparking
        self.speed_delay = speed_delay
        self.heat = bytearray(len(np) // 3)
        # self.num_leds = len(np) // 3

    async def start(self):
        np = self.np
        speed_delay = self.speed_delay
        while True:
            self.fire_once(np)
            await sleep_ms(speed_delay)
            print(struct.unpack('>30B', np))
            # yield np

    def fire_once(self, np):
        num_leds = len(np) // 3
        heat = self.heat
        # Step 1.  Cool down every cell a little
        max_num_cooling = (((self.cooling * 10) // num_leds) + 2)
        for i in range(num_leds):
            cooldown = random.randint(0, max_num_cooling)

            if cooldown >= heat[i]:
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown

        # Step 2.  Heat from each cell drifts 'up' and diffuses a little
        for k in range(num_leds - 1, 2, -1):
            heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) // 3

        # Step 3.  Randomly ignite new 'sparks' near the bottom
        if random.randint(0, 255) < self.sparking:
            y = random.randint(0, 7)
            heat[y] = min(255, heat[y] + random.randint(160, 255))

        # Step 4.  Convert heat to LED colors
        for j in range(num_leds):
            color =self.heat_to_color(heat[j])
            np[j * 3] = color[0]
            np[j * 3 + 1] = color[1]
            np[j * 3 + 2] = color[2]

    @staticmethod
    def heat_to_color(temperature):
        # Scale 'heat' down from 0-255 to 0-191
        t192 = temperature*191//255

        # calculate ramp up from
        heatramp = t192 & 63
        heatramp <<= 2

        val = bytearray(3)

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

        return val

#
# async def consume():
#     loop = asyncio.get_event_loop()
#     t_start = time()
#     while True:
#         note = await queue.get()
#         loop.create_task(pulse(t_start, note))


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    np = bytearray(3*10)
    fire = Fire(np)
    loop.create_task(fire.start())
    # loop.create_task(consume(queue))

    loop.run_forever()
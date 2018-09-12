import random

try:
    import ustruct as struct
except ImportError:
    import struct
# try:
#     import uasyncio as asyncio
# except ImportError:
#     import asyncio


# async def sleep_ms(duration):
#     try:
#         await asyncio.sleep_ms(duration)
#     except AttributeError:
#         await asyncio.sleep(duration/1000)


class Fire:
    def __init__(self, num_leds, cooling=50, sparking=120, speed_delay=20):
        self.cooling = cooling
        self.sparking = sparking
        self.speed_delay = speed_delay
        self.num_leds = num_leds
        self.heat = bytearray(num_leds)

    # def __await__(self):
    #     print('__await__ called')
    #     yield from asyncio.sleep(0)
    #     self.fire_once()  # Other coros get scheduled here
    #     np = self.get_color_array()
    #     ar_ints = struct.unpack('>{}B'.format(self.num_leds*3), np)
    #     ar_leds = [ar_ints[r:r+3] for r in range(0, len(ar_ints),3)]
    #     print(ar_leds)
    #     return np
    #
    # __iter__ = __await__  # See note below

    # async def start(self):
    #     np = self.np
    #     speed_delay = self.speed_delay
    #     while True:
    #         self.fire_once(np)
    #         await sleep_ms(speed_delay)
    #         print(struct.unpack('>30B', np))

    def tick(self):
        self.fire_once()

    def fire_once(self):
        num_leds = self.num_leds
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

    def get_color_array(self, strength=0.05):
        # Step 4.  Convert heat to LED colors
        num_leds = self.num_leds
        np = bytearray(num_leds*4)
        heat = self.heat
        for j in range(num_leds):
            color =self.heat_to_color(heat[j])
            np[j * 4] = int(color[0]*strength)
            np[j * 4 + 1] = int(color[1]*strength)
            np[j * 4 + 2] = int(color[2]*strength)
            np[j * 4 + 3] = 0

        return np

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
import random
try:
    import ustruct as struct
except ImportError:
    import struct
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


class Meteor:
    def get_color_array(self, np, color, meteor_size=5, meteor_trail_decay=64, meteor_random_decay=True, speed_delay=50):
        self.np = np
        self.color = color
        self.meteor_size = meteor_random_decay
        self.meteor_trail_decay = meteor_trail_decay
        self.meteor_random_decay = meteor_random_decay
        self.speed_delay = speed_delay

    async def meteor(self):
        black = bytearray(len(np))
        np = self.np
        self.num_leds = len(np//3)
        np[:] = black
        num_leds = np.n
        meteor_random_decay = self.meteor_random_decay
        meteor_trail_decay = self.meteor_trail_decay
        meteor_size = self.meteor_size
        speed_delay = self.speed_delay
        color = self.color

        for i in range(num_leds*2):
            # fade brightness all LEDs one step
            for j in range(num_leds):
                if not meteor_random_decay or random.randint(0,10)>5:
                    self.fade_to_black(np, j, meteor_trail_decay)

            # draw meteor
            for j in range(meteor_size):
                if i-j < num_leds:
                    np[i-j] = color

            await asyncio.sleep_ms(speed_delay)

    def fade_to_black(self, np, idx, fade_value):
        old_color = np[idx]
        new_color = [c - (c * fade_value // 256) if c > 10 else 0 for c in old_color]
        np[idx] = new_color

from machine import Timer, RTC, Pin
import NeoPixel
from music import Song
from touch import Touch
from time import time
try:
    import umath as mathj
except ImportError:
    import math
try:
    from asyn import Semaphore
except ImportError:
    from asyncio import Semaphore
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from animations.fire import Fire


class Note:
    """
    Beats for a single note
    """
    def __init__(self, duration, steps=34):
        self.duration = duration
        self.steps = steps
        self.dt_tick = steps/duration
        self.t_start = time()
        self.pulses = []
        self.positions = {}

    # def add_pulse(self, note):
    #     self.pulses[note[0]] = 0

    async def pulse(self, note):
        ts = note[0]
        self.pulses.append(ts)
        duration = self.duration
        time_wait = (ts + self.t_start) - time()
        if time_wait >= 0:
            await asyncio.sleep(time_wait-duration)

        steps = self.steps
        for i in range(steps):
            self.positions[ts] = i
            print(i, ts, note[1])
            await asyncio.sleep(duration/steps)


class GameRound:
    def __init__(self, gracetime=0.1):
        self.score = 0
        self.multiplier = bytearray(1)
        self.combo_count = bytearray(1)
        self.t_start = time()
        self.gracetime = gracetime
        self.pulses = {}
        self.np_notes = {}
        self.np_notes[0] = NeoPixel(Pin(17), 34, timing=True)
        self.animations = []
        self.animation_bg = None

    def handle_touch(self, pos, ts):
        accepted = False
        note = self.pulses.get(pos)
        if len(note) > 0:
            pulse = note[0]
            if math.abs(pulse[0] - ts) < self.gracetime:
                accepted = True

        if accepted:
            self.combo_count += 1
            self.multiplier = max(self.combo_count % 10, 1)
            self.score += self.multiplier
        else:
            self.combo_count = 0
        self.animate_touch(pos, accepted)

    def animate_touch(self, pos, accepted):
        print(pos, accepted)

    async def refresh_leds(self, delay=100):
        sleep = asyncio.sleep
        while True:
            np = self.np_notes[0]

            anim_bg = self.animation_bg
            if anim_bg:
                np.buf = anim_bg.get_color_array()

            for note_pos, note in self.pulses.items():
                for i in note.positions:
                    np[i] = (255, 0, 255)

            np.write()
            await sleep(delay)


async def consume(queue, callback):
    while True:
        item = await queue.get()
        await callback(item)


async def queue_put(queue, iterable):
    with iterable as it:
        async for n in it:
            await queue.put(n)

async def loop_stuff(animation):
    while True:
        np = await animation
        await asyncio.sleep(0.1)

async def report_touch(touch, delay=0.5):
    print(touch.istouch)
    await asyncio.sleep(delay)

def main():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(maxsize=8)
    song = Song('dr_chaos')
    loop.create_task(queue_put(queue, song))
    pulse = Note()

    max_concurrent = 8
    for _ in range(max_concurrent):
        loop.create_task(consume(queue, pulse.pulse))

    fire_anim = Fire(num_leds=10)
    loop.create_task(loop_stuff(fire_anim))

    touch_pins = [1,2,3]
    touch = Touch(touch_pins)
    timer = Timer(0)
    timer.init(period=100, mode=Timer.PERIODIC, callback=touch.cb)
    loop.create_task(report_touch(touch))

    # import esp
    # esp.neopixel_write(pin, grb_buf, is800khz)
    # rtc = RTC()
    # rtc.datetime()
    loop.run_forever()

if __name__ == "__main__":
    main()
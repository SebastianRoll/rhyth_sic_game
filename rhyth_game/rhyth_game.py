from music import Song
from time import time
try:
    from asyn import Semaphore
except ImportError:
    from asyncio import Semaphore
from animations.fire import Fire

class Pulse:
    def __init__(self):
        self.t_start = time()

    async def pulse(self, note):
        duration = 1
        time_wait = (note[0] + self.t_start) - time()
        if time_wait >= 0:
            await asyncio.sleep(time_wait-duration)
        # t_deviation = time()-(t_start+t_play[0])
        parts = 3
        for i in range(parts):
            print(i, note[0], note[1])
            await asyncio.sleep(duration/parts)


async def consume(queue, callback):
    while True:
        item = await queue.get()
        await callback(item)


async def queue_put(queue, iterable):
    async for n in iterable:
        await queue.put(n)

async def loop_stuff(animation):
    while True:
        np = await animation
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(maxsize=8)
    song = Song()
    loop.create_task(queue_put(queue, song))
    pulse = Pulse()

    max_concurrent = 8
    for _ in range(max_concurrent):
        loop.create_task(consume(queue, pulse.pulse))

    fire_anim = Fire(num_leds=10)
    loop.create_task(loop_stuff(fire_anim))

    loop.run_forever()
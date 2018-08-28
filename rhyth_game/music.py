import uasyncio as asyncio

class MusicMock:
    def __init__(self):
        loop = asyncio.get_event_loop()

    async def play(self):
        pass

    async def record(self, queue, filename='default.txt'):
        while True:
            result = await queue.get()
            print("RECORDING {}".format(result))
        return
        with open(filename, 'wb') as f:
            while True:
                result = await queue.get()
                f.write(result)


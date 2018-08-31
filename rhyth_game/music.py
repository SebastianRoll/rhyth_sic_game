from time import time, sleep
from songs.chaos import dr_chaos

# import pandas as pd
# df = pd.DataFrame(song['charts'][2]['notes'], columns=['time', 'note'])

class Song:
    def __init__(self):
        self.song_dict = dr_chaos
        self.index = 0
        self.notes = self.song_dict['charts'][0]['notes']

    async def __aiter__(self):
        return self

    async def __anext__(self):
        beat = await self.get_beat()
        if beat:
            return beat
        else:
            raise StopAsyncIteration

    async def get_beat(self):
        if self.index >= len(self.notes):
            return None
        beat = self.notes[self.index]
        self.index += 1
        return beat

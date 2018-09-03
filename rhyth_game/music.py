import os
from time import time, sleep
from songs.dr_chaos.meta import dr_chaos

# import pandas as pd
# df = pd.DataFrame(song['charts'][2]['notes'], columns=['time', 'note'])


class Song:
    def __init__(self, path):
        self.song_dict = dr_chaos
        self.index = 0
        self.path = path
        self.notes = self.song_dict['charts'][0]['notes']
        self.open_file = None

    def __enter__(self):
        self.open_file = open(os.path.join('songs',self.path,'easy.csv'), 'r')
        self.open_file.readline()
        return self

    def __exit__(self, *args):
        self.open_file.close()

    async def __aiter__(self):
        return self

    async def __anext__(self):
        beat = await self.get_beat()
        if beat:
            return beat
        else:
            raise StopAsyncIteration

    async def get_beat(self):
        beat = self.open_file.readline()
        return beat

    async def get_beat_old(self):
        if self.index >= len(self.notes):
            return None
        beat = self.notes[self.index]
        self.index += 1
        return beat

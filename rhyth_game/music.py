
# import pandas as pd
# df = pd.DataFrame(song['charts'][2]['notes'], columns=['time', 'note'])

from time import time, sleep
from songs.chaos import dr_chaos


class Song:
    def __init__(self):
        self.song_dict = dr_chaos

    async def __aiter__(self):
        return self

    async def __anext__(self):
        notes = self.song_dict['charts'][0]['notes']
        for n in notes:
            return n
        raise StopAsyncIteration


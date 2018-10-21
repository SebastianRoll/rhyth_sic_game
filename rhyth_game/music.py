# from songs.dr_chaos.meta import dr_chaos
# from songs.dr_chaos.meta import dr_chaos
from songs.boom_clap.meta import meta as dr_chaos
# import os
from utils import timed_function
import ustruct

class Song:
    def __init__(self, title, difficulty='medium'):
        self.song_dict = dr_chaos
        self.index = 0
        self.title = title
        # self.notes = self.song_dict['charts'][0]['notes']
        self._open_file = None
        self.difficulty = difficulty
        self.beat_ms_before_hit = 750

    def __enter__(self):
        path = 'songs/' + self.title +'/{}.csv'.format(self.difficulty)
        # self._open_file = path = '/'.join('songs', self.title, '{}.csv'.format(self.difficulty))
        # self.open_file = open(os.path.join('songs', self.title, '{}.csv'.format(self.difficulty)), 'r')
        # self._open_file = open('{}.csv'.format(self.difficulty), 'r')
        self._open_file.readline()
        return self

    def __exit__(self, *args):
        self._open_file.close()

    async def __aiter__(self):
        return self

    async def __anext__(self):
        beat = await self.get_beat()
        beat = [float(el) for el in beat.strip('\n').split(',')]
        if beat:
            return beat
        else:
            raise StopAsyncIteration

    def open_file(self):
        path = 'songs/' + self.title +'/{}.b'.format(self.difficulty)
        print(path)
        self._open_file = open(path, 'rb')

    def close_file(self):
        self._open_file.close()

    def read_beat(self):
        return self._open_file.read(8)

    def readline(self):
        return self._open_file.readline()

    def next(self):
        beat = self.read_beat()
        if not beat:
            return None
        (ts, *notebytes)= ustruct.unpack('>f4B', beat)
        ts = ts*1000
        notebytes = [chr(n) for n in notebytes]
        notebytes = [i for i, n in enumerate(list(notebytes)) if n != '0']
        return ts, notebytes

    async def get_beat(self):
        beat = self._open_file.readline()
        return beat

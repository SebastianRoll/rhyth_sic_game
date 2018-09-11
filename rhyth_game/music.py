# from songs.dr_chaos.meta import dr_chaos
# from songs.dr_chaos.meta import dr_chaos
from songs.boom_clap.meta import meta as dr_chaos
from songs import song_list
# import os
# from utils import timed_function

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
        path = 'songs/' + self.title +'/{}.csv'.format(self.difficulty)
        # path = '/'.join('songs', self.title, '{}.csv'.format(self.difficulty))
        print(path)
        self._open_file = open(path, 'r')
        self._open_file.readline()

    def close_file(self):
        self._open_file.close()

    # @timed_function
    def next(self):
        beat = self._open_file.readline()
        # print(beat)
        if beat is "":
            return None
        ts, notebytes = beat.strip('\n').split(',')
        ts = float(ts)*1000
        notebytes = [i for i, n in enumerate(list(notebytes)) if n is not '0']
        if beat:
            return ts, notebytes
        else:
            raise NotImplemented

    async def get_beat(self):
        beat = self._open_file.readline()
        return beat

    # async def get_beat_old(self):
    #     if self.index >= len(self.notes):
    #         return None
    #     beat = self.notes[self.index]
    #     self.index += 1
    #     return beat


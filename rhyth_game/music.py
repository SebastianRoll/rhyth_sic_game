import os
from songs.dr_chaos.meta import dr_chaos
from songs import song_list
from yx5300 import mp3


class Song:
    def __init__(self, path):
        self.song_dict = dr_chaos
        self.index = 0
        self.path = path
        self.notes = self.song_dict['charts'][0]['notes']
        self.open_file = None
        self.difficulty = 'easy'

    def __enter__(self):
        self.open_file = open(os.path.join('songs',self.path,'{}.csv'.format(self.difficulty)), 'r')
        self.open_file.readline()
        return self

    def __exit__(self, *args):
        self.open_file.close()

    async def __aiter__(self):
        return self

    async def __anext__(self):
        beat = await self.get_beat()
        beat = [float(el) for el in beat.strip('\n').split(',')]
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


class SongMenu:
    def __init__(self, title='dr_chaos'):
        self.title = title
        self.song = Song(title)

    def play(self):
        mp3.play_track(song_list[self.title])
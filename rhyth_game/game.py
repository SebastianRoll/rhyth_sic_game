import utime as time

import music

class LastBeatSent(Exception):
    pass


class Points:
    def __init__(self):
        self.hits = 0
        self.score = 0
        self.multiplier = 0
        self.combo_count = 0

    def hit(self):
        try:
            self.hits += 1
            self.combo_count += 1
            self.multiplier = max(self.combo_count // 3, 1)
            self.score += self.multiplier
            # print(self.score, self.multiplier)
        except Exception as e:
            print(e)
            raise

    def miss(self):
        self.combo_count = 0
        self.score -= 1
        # print(self.score, self.multiplier)


class Game:
    def __init__(self, song_title, difficulty='easy', debug=False):
        self.debug = debug
        self.song = music.Song(song_title, difficulty=difficulty)
        self.points = Points()
        # self.mp3 = Mp3()

        # beats
        self.beat_buffer = {k:[] for k in range(8)}

        # time
        self.time = time.ticks_ms
        self.ts_start = self.time()

        self.time_window_max = 200

        # Beats buffer
        self.beat_last_ts = 0
        self.beat_buffer_padding_ms = 500

    def time_passed(self):
        return self.time() - self.ts_start

    def fill_beat_buffer(self):
        time_expired = self.time_passed()
        song = self.song
        beat_buffer_ms = self.song.beat_ms_before_hit + self.beat_buffer_padding_ms
        # print("filling beat buffer")
        while True:
            # print(abc, beat_buffer_ms, time_expired + beat_buffer_ms)
            if self.beat_last_ts <= time_expired + beat_buffer_ms:
                beat = song.next()
                if self.debug:
                    print(beat)
                if beat is None:
                    raise LastBeatSent("Song finished")
                ts, notes = beat
                # print(ts, notes)
                for note in notes:
                    self.add_beat(note, ts)
                self.beat_last_ts = ts
            else:
                # print("BEAT BUFFER", self.beat_buffer)
                return

    def purge_stale_beats(self):
        time_window = 0
        time_window_max = self.time_window_max
        time_passed = self.time_passed()
        for beats in self.beat_buffer.values():
            while True:
                if len(beats) > 0:
                    oldest_ts = beats[0]
                    time_window = time_passed - oldest_ts
                    if time_window > time_window_max:
                        # print("MISS PURGE")
                        beats.pop(0)
                        self.points.miss()
                    else:
                        break
                else:
                    break

    def handle_hit(self, note, touch_ts):
        hit = False
        beats = self.beat_buffer[note]
        time_window = 0
        time_window_max = self.time_window_max
        for idx, oldest_ts in enumerate(beats):
            # oldest_ts = beats.pop(0)
            time_window = touch_ts - oldest_ts
            # print('window', time_window, touch_ts, oldest_ts)
            if time_window > time_window_max:
                continue
            elif abs(time_window) <= time_window_max:
                # HIT
                hit = True
                beats.pop(idx)
                break
            else:
                # MISS
                break
        if hit:
            self.points.hit()
        else:
            self.points.miss()
        return hit

    def add_beat(self, note, ts):
        self.beat_buffer[note].append(ts)

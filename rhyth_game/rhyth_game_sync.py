import time
import music
from songs import song_list
from yx5300.mp3_rhythgame import Mp3

class Points:
    def __init__(self):
        self.score = 0
        self.multiplier = bytearray(1)
        self.combo_count = bytearray(1)

    def hit(self):
        self.combo_count += 1
        self.multiplier = max(self.combo_count % 10, 1)
        self.score += self.multiplier

    def miss(self):
        self.combo_count = 0


class Game:
    def __init__(self, song_title):
        self.song = music.Song(song_title)
        self.points = Points()
        self.mp3 = Mp3()

        # beats
        self.notes_beats = {k:[] for k in range(8)}

        # time
        self.time = time.time
        self.ts_start = self.time()
        self.time_window_max = 0.1

        # Beats buffer
        self.beat_last_ts = 0
        self.beat_buffer_padding_ms = 300

    def start(self):
        self.mp3.play_track(song_list[self.song.title])
        self.ts_start = self.time()
        raise NotImplementedError

    @property
    def time_expired(self):
        return self.time() - self.ts_start

    def fill_beat_buffer(self):
        time_expired = self.time_expired
        song = self.song
        beat_buffer_ms = self.song.beat_ms_before_hit + self.beat_buffer_padding_ms
        while True:
            if self.beat_last_ts - time_expired <= beat_buffer_ms:
                note, ts = song.next()
                self.add_beat(note, ts)
                self.beat_last_ts = ts
            else:
                return

    def handle_hit(self, note, touch_ts):
        hit = False
        beats = self.notes_beats[note]
        time_window = 0
        time_window_max = self.time_window_max
        if len(beats) > 0:
            while True:
                oldest_ts = beats.pop()
                time_window = touch_ts - oldest_ts
                if time_window > time_window_max:
                    continue
                elif abs(time_window) <= time_window_max:
                    # HIT
                    hit = True
                else:
                    # MISS
                    pass
                break
        if hit:
            self.points.hit()
        else:
            self.points.miss()

    def add_beat(self, note, ts):
        self.notes_beats[note].append(ts)


class RhythGame:
    def __init__(self, touch_driver=None):
        self.touch_driver = touch_driver
        self.game = None
        # LED memory view - Outer
        self.outer = bytearray(220*3) #, "ascii")
        self.outer_mv = memoryview(self.outer)
        self.outer_leds = {
            'top': self.outer_mv[:110*3],
            'bot': self.outer_mv[110*3:]
        }

        # LED memory view - Note pins
        led_count = 68
        self.led_count = led_count
        self.ws2812 = bytearray(4*led_count)
        self.ws2812_mv = memoryview(self.ws2812)
        self.ws2813 = bytearray(4*led_count)
        self.ws2813_mv = memoryview(self.ws2813)

        # LED memory view - Notes
        self.notes_led = {}
        # ws2812
        for i in range(1, 4):
            self.notes_led[i] = self.ws2812_mv[(i-1)*led_count:i*led_count]
        # ws2813
        for i in range(1, 4):
            self.notes_led[i+4] = self.ws2813_mv[(i-1)*led_count:i*led_count]

        # Animations
        self.notes_anim = {k:None for k in range(8)}
        self.outer_anim = {
            'top': None,
            'bot': None
        }

    def play_song(self, title='dr_chaos'):
        self.game = Game(title)
        touch_driver = self.touch_driver
        with self.game.song as s:
            while True:
                self.game.fill_beat_buffer()
                self.tick_animation()
                self.refresh_leds()
                if touch_driver:
                    notes_hit = touch_driver.cb()
                    for note in notes_hit:
                        self.game.handle_hit(note, self.game.time())

    def get_beat_positions(self, note_id):
        """
        Calculates led position for pulses on specified note
        :param note_id:  specified note id
        :return: pulse positions [list]
        """
        positions = []
        time_expired = self.game.time_expired
        time_delta_ms = 0
        steps = len(self.led_count//3)
        beat_ms_before_hit = self.game.song.beat_ms_before_hit
        steps_per_ms = steps//beat_ms_before_hit
        beats = self.game.notes_beats[note_id]
        for beat_ts in beats[::-1]:
            time_delta_ms = time_expired - beat_ts
            if time_delta_ms > 0 or time_delta_ms < beat_ms_before_hit:
                break
            pos = time_delta_ms * steps_per_ms
            positions.append(pos)
        return positions

    def refresh_leds(self):
        """
        Updates the bytearray buffers, but does not send the buffer to NeoPixel pin.
        :return: None
        """
        notes_anim = self.notes_anim

        # load note animation
        for note_id, mv in self.notes_led.items():
            anim = notes_anim[note_id]
            if anim:
                mv[:] = anim.get_color_array()

            positions = self.get_beat_positions(note_id)
            for pos in positions:
                mv[pos:pos+3] = (0,0,255) # [0,0,255]

        # load outer animation
        outer_anim = self.outer_anim
        for note_id, mv in self.outer_leds.items():
            anim = outer_anim[note_id]
            if anim:
                mv[:] = anim.get_color_array()

    def tick_animation(self):
        anims = set(self.notes_anim.values() + self.notes_led.values())
        [a.tick() for a in anims if a is not None]
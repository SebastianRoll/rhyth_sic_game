from machine import Pin
try:
    import utime as time
except ImportError:
    import time

import music
# from songs import song_list
song_list = {
    'dr_chaos': 1,
}
from neopixel import NeoPixel
from mp3_rhythgame import Mp3

from fire import Fire

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
        self.beat_buffer = {k:[] for k in range(8)}

        # time
        self.time = time.time
        self.ts_start = self.time()
        self.time_window_max = 100

        # Beats buffer
        self.beat_last_ts = 0
        self.beat_buffer_padding_ms = 300

    def start(self):
        self.mp3.play_track(song_list[self.song.title])
        self.ts_start = self.time()
        raise NotImplementedError

    def time_expired(self):
        return (self.time() - self.ts_start) * 1000

    def fill_beat_buffer(self):
        time_expired = self.time_expired()
        song = self.song
        beat_buffer_ms = self.song.beat_ms_before_hit + self.beat_buffer_padding_ms
        # print("filling beat buffer")
        abc = bytearray(1)
        while True:
            abc = self.beat_last_ts
            # print(abc, beat_buffer_ms, time_expired + beat_buffer_ms)
            if abc <= time_expired + beat_buffer_ms:
                ts, notes= song.next()
                # print(ts, notes)
                for note in notes:
                    self.add_beat(note, ts)
                self.beat_last_ts = ts
            else:
                # print("BEAT BUFFER", self.beat_buffer)
                return

    def handle_hit(self, note, touch_ts):
        hit = False
        beats = self.beat_buffer[note]
        time_window = 0
        time_window_max = self.time_window_max
        while True:
            if len(beats) > 0:
                oldest_ts = beats.pop(0)
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
            else:
                break
        if hit:
            print("HIT")
            self.points.hit()
        else:
            print("MISS")
            self.points.miss()

    def add_beat(self, note, ts):
        self.beat_buffer[note].append(ts)


class RhythGame:
    def __init__(self, touch_driver=None):
        self.touch_driver = touch_driver
        self.game = None
        # LED memory view - Outer
        self.outer = bytearray(220*4) #, "ascii")
        self.outer_np = NeoPixel(Pin(16), 220, bpp=4, timing=True)
        self.outer_mv = memoryview(self.outer)
        self.outer_leds = {
            'top': self.outer_mv[:110*3],
            'bot': self.outer_mv[110*3:]
        }

        # LED memory view - Note pins
        led_count = 34*3
        self.led_count = led_count
        self.ws2812 = bytearray(4*led_count)
        self.ws2812_np = NeoPixel(Pin(17), 34*4, bpp=3, timing=True)
        self.ws2812_mv = memoryview(self.ws2812)

        self.ws2813 = bytearray(4*led_count)
        self.ws2813_mv = memoryview(self.ws2813)
        self.ws2813_np = NeoPixel(Pin(5), 34*4, bpp=3, timing=True)

        # LED memory view - Notes
        self.notes_led = {}
        # ws2812
        for i in range(4):
            self.notes_led[i] = self.ws2812_mv[i*led_count:(i+1)*led_count]
        # ws2813
        for i in range(4):
            self.notes_led[i+4] = self.ws2813_mv[i*led_count:(i+1)*led_count]

        # Animations
        self.notes_anim = {k:None for k in range(8)}
        self.outer_anim = {
            'top': None,
            'bot': None
        }

        # fire = Fire(len(self.outer_leds['top'])//3)
        # self.notes_anim[1] = fire
        # self.notes_anim[4] = fire

    def load_song(self, title='dr_chaos'):
        self.game = Game(title)

    def play_song(self, title='dr_chaos'):
        self.game = Game(title)
        touch_driver = self.touch_driver
        self.game.song.open_file()
        o = 0
        while True:
            try:
                o += 1
                print(self.game.time_expired(), o)
                self.game.fill_beat_buffer()
                self.tick_animation()
                self.refresh_leds()
                if touch_driver:
                    notes_hit = touch_driver.cb()
                    # print('touch', notes_hit)
                    for note in notes_hit:
                        self.game.handle_hit(note, self.game.time())
                self.ws2812_np.buf = self.ws2812
                self.ws2812_np.write()
                self.ws2813_np.buf = self.ws2813
                self.ws2813_np.write()
                self.outer_np.buf = self.outer
                self.outer_np.write()
            except NotImplemented:
                self.game.song.close_file()
                break

    def get_beat_positions(self, note_id, time_expired):
        """
        Calculates led position for pulses on specified note
        :param note_id:  specified note id
        :return: pulse positions [list]
        """
        positions = []
        time_delta_ms = 0
        steps = self.led_count//3
        beat_ms_before_hit = self.game.song.beat_ms_before_hit
        steps_per_ms = steps/beat_ms_before_hit
        beats = self.game.beat_buffer[note_id]
        for beat_ts in beats:
            time_delta_ms = beat_ts - time_expired
            # print(time_delta_ms, time_expired, beat_ts)
            if time_delta_ms < 0 or time_delta_ms > beat_ms_before_hit:
                # print('break')
                break
            pos = int(steps - (time_delta_ms * steps_per_ms))
            if pos <= steps:
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

            # led - note positions
            time_expired = self.game.time_expired()
            positions = self.get_beat_positions(note_id, time_expired)
            if len(positions) > 0:
                print("POS", note_id, positions, time_expired)
            for pos in positions:
                # mv[pos:pos+3] = (0,0,255) # [0,0,255]
                mv[pos] = 0
                mv[pos+1] = 0
                mv[pos+2] = 255

        # load outer animation
        outer_anim = self.outer_anim
        for note_id, mv in self.outer_leds.items():
            anim = outer_anim[note_id]
            if anim:
                mv[:] = anim.get_color_array()

    def tick_animation(self):
        anims = set(list(self.notes_anim.values()) + list(self.outer_anim.values()))
        [a.tick() for a in anims if a is not None]
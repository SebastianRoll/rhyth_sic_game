from machine import Pin, UART
try:
    import utime as time
except ImportError:
    import time
from utils import timed_function
import music
# from songs import song_list
song_list = {
    'dr_chaos': 1,
}
from machine import Neopixel
#from mp3_player.mp3_rhythgame import Mp3
#import mp3

uart = UART(2, baudrate=9600, rx=32, tx=25, timeout=10)
import mp3_player.yx5300 as cmd
uart.write(cmd.set_volume(15))
def play(delay_ms=100):
    uart.write(cmd.play_track(1))
    time.sleep_ms(delay_ms)


# from animations.fire import Fire
class LastBeatSent(Exception):
    pass


class SongFinished(Exception):
    pass


class NeoPixel(Neopixel):
    def set_buffer(self, buf, brightness=255):
        # ar_ints = ustruct.unpack('>{}B'.format(34*4 * 3), buf)
        # ar_leds = [ar_ints[r:r + 3] for r in range(0, len(ar_ints), 3)]
        # print(ar_leds)
        for led_pos in range(len(buf)//3):
            rgb_buf = buf[led_pos*3:led_pos*3+3]
            rgb_int = int.from_bytes(rgb_buf, 'big')
            self.set(led_pos+1, rgb_int, update=False)
        self.brightness(brightness, update=False)
        self.show()


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

        self.time_window_max = 250

        # Beats buffer
        self.beat_last_ts = 0
        self.beat_buffer_padding_ms = 1000

    def time_passed(self):
        return self.time() - self.ts_start

    # @timed_function
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

    # @timed_function
    def add_beat(self, note, ts):
        self.beat_buffer[note].append(ts)


class RhythGame:
    def __init__(self, pin_ws2812, pin_ws2813, pin_outer, touch_driver=None, brightness=255, debug=False, switch_led=False):
        self.debug = debug
        self.brightness = brightness
        self.touch_driver = touch_driver
        self.game = None
        # LED memory view - Outer
        self.outer = bytearray(220*4) #, "ascii")
        self.outer_np = NeoPixel(Pin(pin_outer), 220, Neopixel.TYPE_RGBW)
        self.outer_mv = memoryview(self.outer)
        self.outer_leds = {
            'top': self.outer_mv[:110*3],
            'bot': self.outer_mv[110*3:]
        }

        # LED memory view - Note pins
        led_count = 34*3
        self.led_count = led_count
        self.ws2812 = bytearray(4*led_count)
        self.ws2812_np = NeoPixel(Pin(pin_ws2812), 34*4)
        self.ws2812_np.clear()
        self.ws2812_mv = memoryview(self.ws2812)

        self.ws2813 = bytearray(4*led_count)
        self.ws2813_np = NeoPixel(Pin(pin_ws2813), 34*4) #5
        ((T1H, T1L), (T0H, T0L), Treset) = [(580, 220), (220, 580), 280000]  # WORKS PERFECTLY FOR WS2813!
        self.ws2813_np.timings([(T1H, T1L), (T0H, T0L), Treset])
        self.ws2813_np.clear()
        self.ws2813_mv = memoryview(self.ws2813)

        # LED memory view - Notes
        self.notes_led = {}


        # ws2812
        for i in range(4):
            if switch_led:
                self.notes_led[i] = self.ws2812_mv[i*led_count:(i+1)*led_count]
            else:
                self.notes_led[i+4] = self.ws2812_mv[i*led_count:(i+1)*led_count]

        # ws2813
        for i in range(4):
            if switch_led:
                self.notes_led[i+4] = self.ws2813_mv[i * led_count:(i + 1) * led_count]
            else:
                self.notes_led[i] = self.ws2813_mv[i * led_count:(i + 1) * led_count]

        # self.ring_led = self.ws2812_mv[-12:]

        # Animations
        self.notes_anim = {k:None for k in range(8)}
        self.outer_anim = {
            'top': None,
            'bot': None
        }

        # fire = Fire(34)
        # self.notes_anim[1] = fire
        # self.notes_anim[4] = fire

    def play_song(self, title='dr_chaos', delay_ms=500, difficulty='easy'):
        self.game = Game(title, difficulty=difficulty, debug=self.debug)
        touch_driver = self.touch_driver
        self.game.song.open_file()
        o = 0
        # play(delay_ms=delay_ms)
        started = False
        last_active_ts = -1
        self.game.ts_start = self.game.time()
        while True:
            if not started and self.game.time_passed() > delay_ms:
                play()
                started = True
            try:
                # print('time expired:', self.game.time_passed(), o)
                if o % 10 == 0:
                    self.game.purge_stale_beats()
                    try:
                        self.game.fill_beat_buffer()
                    except LastBeatSent:
                        last_active_ts = self.game.beat_last_ts
                    if last_active_ts > 0 and self.game.time_passed() > self.game.beat_last_ts:
                        self.game.song.close_file()
                        self.ws2813_np.clear()
                        time.sleep_ms(50)
                        self.ws2813_np.deinit()
                        print("You stuck!", self.game.points.score)
                        break
                self.tick_animation()
                self.refresh_leds()
                if touch_driver:
                    notes_hit = touch_driver.cb()
                    for note in notes_hit:
                        # print('touch', note)
                        was_hit = self.game.handle_hit(note, self.game.time_passed())
                        mv = self.notes_led[note]
                        if was_hit:
                            mv[-3] = 0x00
                            mv[-2] = 0xFF
                            mv[-1] = 0x00
                        else:
                            mv[-3] = 0xFF
                            mv[-2] = 0x00
                            mv[-1] = 0x00
                # reverse leds
                self.reverse_leds()

                self.ws2813_np.set_buffer(self.ws2813, brightness=self.brightness)
                self.ws2812_np.set_buffer(self.ws2812, brightness=self.brightness)
                # self.ws2813_np.buf = self.ws2813
                # self.ws2813_np.write()
                # self.outer_np.buf = self.outer
                # self.outer_np.write()
                o += 1
            except Exception as e:
                print("You stuck", self.game.points.score)
                print(e)
                self.game.song.close_file()
                raise

    def reverse_leds(self):
        for note, mv in self.notes_led.items():
            if note % 2 is 1:
                mv[:] = bytearray(reversed(mv))

    def get_beat_positions(self, note_id, time_passed):
        """
        Calculates led position for pulses on specified note
        :param note_id:  specified note id
        :return: pulse positions [list]
        """
        positions = []
        time_delta_ms = 0
        steps = (self.led_count//3) - 1
        beat_ms_before_hit = self.game.song.beat_ms_before_hit
        steps_per_ms = steps/beat_ms_before_hit
        beats = self.game.beat_buffer[note_id]
        for beat_ts in beats:
            time_delta_ms = beat_ts - time_passed
            # print(time_delta_ms, time_passed, beat_ts)
            if time_delta_ms < 0 or time_delta_ms > beat_ms_before_hit:
                continue
            pos = int(steps - (time_delta_ms * steps_per_ms))
            if pos <= steps:
                positions.append(pos)
        return positions

    def refresh_leds(self):
        """
        Updates the bytearray buffers, but does not send the buffer to Neopixel pin.
        :return: None
        """

        # clear previous buffer
        self.ws2812[:] = bytearray(len(self.ws2812))
        self.ws2813[:] = bytearray(len(self.ws2813))
        notes_anim = self.notes_anim

        for note_id, mv in self.notes_led.items():
            # load note animation
            anim = notes_anim[note_id]
            if anim:
                mv[:] = anim.get_color_array()

            # led - note positions
            time_passed = self.game.time_passed()
            positions = self.get_beat_positions(note_id, time_passed)
            # if len(positions) > 0:
            #     print("POS", note_id, positions, time_expired)
            for pos in positions:
                if pos < 0 or pos > 33:
                    print("POS IS", pos)
                if note_id % 4 == 0:
                    mv[(pos) * 3] = 0xCC
                    mv[(pos) * 3 + 1] = 0xCC
                elif note_id % 4 == 1:
                    mv[(pos)*3+1] = 0xFF
                elif note_id % 4 == 2:
                    mv[(pos)*3+2] = 0xFF
                elif note_id % 4 == 3:
                    mv[(pos) * 3] = 0xCC
                    mv[(pos)*3+2] = 0xCC
            mv[-3] = 0xFF
            mv[-2] = 0xFF
            mv[-1] = 0xFF


        # load outer animation
        outer_anim = self.outer_anim
        for note_id, mv in self.outer_leds.items():
            anim = outer_anim[note_id]
            if anim:
                mv[:] = anim.get_color_array()

    def tick_animation(self):
        anims = set(list(self.notes_anim.values()) + list(self.outer_anim.values()))
        [a.tick() for a in anims if a is not None]

    def clean_up(self):
        print("cleaning up..")
        self.ws2813_np.clear()
        self.ws2812_np.clear()
        self.outer_np.clear()
        time.sleep_ms(500)
        self.ws2813_np.deinit()
        self.ws2812_np.deinit()
        self.outer_np.deinit()

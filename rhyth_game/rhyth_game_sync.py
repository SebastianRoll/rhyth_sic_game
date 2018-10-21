
from utils import timed_function
import ustruct
import music
from array import array
# from songs import song_list
#from mp3_player.mp3_rhythgame import Mp3
#import mp3
from machine import Pin, UART, Neopixel
import utime as time
import pin_definitions as p
uart = UART(2, baudrate=9600, rx=p.pin_uart2_rx, tx=p.pin_uart2_tx, timeout=10)
import mp3_player.yx5300 as cmd
uart.write(cmd.set_volume(30))
def play(track, delay_ms=100):
    uart.write(cmd.play_track(track))
    time.sleep_ms(delay_ms)


def mp3_reset():
    uart.write(cmd.reset_module())


# from animations.fire4 import Fire
class LastBeatSent(Exception):
    pass


class SongFinished(Exception):
    pass



class NeoPixel(Neopixel):
    def __init__(self, pin, pixels, type=Neopixel.TYPE_RGB):
        self.buf = array('L', pixels)
        super().__init__(pin, pixels, type)


    # @timed_function
    def set_buffer(self, buf):
        old_buf = self.buf
        # ar_ints = ustruct.unpack('>{}B'.format(34*4 * 3), buf)
        # ar_leds = [ar_ints[r:r + 3] for r in range(0, len(ar_ints), 3)]
        # print(ar_leds)
        # for i in range(len(buf)):
        #     for b in ustruct.unpack_from('>3c', buf, i):
        #         self.set(i, b, update=False)

        # set = self.set
        # for i, c in enumerate(buf):
        #     set(i, c, update=False)

        for led_pos in range(len(buf)):
            c = int(buf[led_pos]) & 0xFFFFFF
            self.set(led_pos + 1, c, update=False)
            # if old_buf[led_pos] !=  buf[led_pos]:
            #     print(led_pos, buf[led_pos])
            #     c = int(buf[led_pos]) & 0xFFFFFF
            #     self.set(led_pos+1, c, update=False)
        # for led_pos in r:
        #     rgb_buf[:] = buf[led_pos*3:led_pos*3+3]
        #     rgb_int[0] = int.from_bytes(rgb_buf, 'big')
        #     self.set(led_pos+1, rgb_int[0], update=False)
        self.show()
        self.buf = buf
        time.sleep_ms(10)


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

    # @timed_function
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
    def __init__(self, pin_ws2812, pin_ws2813, pin_outer, touch_driver=None, brightness=255, debug=False, song_list=None):
        self.song_list = song_list
        self.debug = debug
        self.brightness = brightness
        self.touch_driver = touch_driver
        self.game = None
        # LED memory view - Outer
        self.outer = array('L', 220)
        self.outer_np = NeoPixel(Pin(pin_outer), 220, Neopixel.TYPE_RGBW)
        self.outer_mv = memoryview(self.outer)
        self.outer_leds = {
            'top': self.outer_mv[:110*4],
            'bot': self.outer_mv[110*4:]
        }

        # LED memory view - Note pins
        led_count = 34
        self.led_count = led_count
        self.ws2812 = array('L', 4*led_count)
        self.ws2812_np = NeoPixel(Pin(pin_ws2812), 34*4)
        self.ws2812_np.clear()
        self.ws2812_mv = memoryview(self.ws2812)

        self.ws2813 = array('L', 4*led_count)
        self.ws2813_np = NeoPixel(Pin(pin_ws2813), 34*4) #5

        # -- DON'T USE TIMINGS ANYMORE!
        # ((T1H, T1L), (T0H, T0L), Treset) = [(580, 220), (220, 580), 280000]  # WORKS PERFECTLY FOR WS2813!
        #self.ws2813_np.timings([(T1H, T1L), (T0H, T0L), Treset])

        self.ws2813_np.clear()
        self.ws2813_mv = memoryview(self.ws2813)

        # LED memory view - Notes
        self.notes_led = {}

        # temp stuff
        self.notes_pos = {}
        r = range(4)
        for i in r:
            self.notes_pos[i] = range(i*34,i*34+34,1-(i%2)*2)
            self.notes_led[i] = self.ws2812_mv[i*led_count:(i+1)*led_count]

        r = range(4)
        # ws2812
        for i in r:
            self.notes_led[i] = self.ws2812_mv[i*led_count:(i+1)*led_count]

        # ws2813
        r = range(4)
        for i in r:
            self.notes_led[i+4] = self.ws2813_mv[i * led_count:(i + 1) * led_count]

        # self.ring_led = self.ws2812_mv[-12:]

        # Animations
        self.notes_anim = {k:None for k in range(8)}
        self.outer_anim = {
            'top': None,
            'bot': None
        }

        # fire = Fire(110)
        # self.outer_anim['top'] = fire
        # self.outer_anim['bot'] = fire
        # self.notes_anim[1] = fire
        # self.notes_anim[4] = fire

    def play_song(self, title='dr_chaos', delay_ms=500, difficulty='easy'):
        game = Game(title, difficulty=difficulty, debug=self.debug)
        touch_driver = self.touch_driver
        touch_count = len(touch_driver.touchpads)
        game.song.open_file()
        self.game = game
        o = 0
        # play(delay_ms=delay_ms)
        started = False
        last_active_ts = -1
        self.game.ts_start = self.game.time()
        is_hit = False
        is_miss = False
        while True:
            if not started and game.time_passed() > delay_ms:
                play(self.song_list[title])
                started = True
            try:
                # print('time expired:', self.game.time_passed(), o)
                if o % 10 == 0:
                    game.purge_stale_beats()
                    try:
                        game.fill_beat_buffer()
                    except LastBeatSent:
                        last_active_ts = game.beat_last_ts
                    if last_active_ts > 0 and game.time_passed() > game.beat_last_ts:
                        game.song.close_file()
                        self.clear_after_song()
                        print("Score:", game.points.score, "hits:", game.points.hits)
                        break
                self.tick_animation()
                self.refresh_leds()
                is_hit = False
                is_miss = False
                if touch_driver:
                    pads_hit = touch_driver.cb()
                    # pads_hit = [touch_driver.check_touch(o % touch_count)]
                    for note in pads_hit:
                        # print('touch', note)
                        was_hit = game.handle_hit(note, game.time_passed())
                        mv = self.notes_led[note]
                        if was_hit:
                            is_hit = True
                            mv[-1] = 0x00FF00
                        else:
                            is_miss = True
                            mv[-1] = 0xFF0000

                self.refresh_outer_leds(is_hit, is_miss)
                # time.sleep_ms(10)

                # reverse leds
                self.reverse_leds()

                self.ws2812_np.set_buffer(self.ws2812)
                self.ws2813_np.set_buffer(self.ws2813)

                o += 1
            except Exception as e:
                print("You stuck", game.points.score)
                print(e)
                game.song.close_file()
                raise

    # @timed_function
    def refresh_outer_leds(self, is_hit, is_miss):
        if is_hit:
            self.outer_np.set(0, 0x000F00, num=220)
        elif is_miss:
            self.outer_np.set(0, 0x0F0000, num=220)
        else:
            self.outer_np.clear()

    def reverse_leds(self):
        for note, mv in self.notes_led.items():
            if note % 2 is 1:
                mv[:] = array('L', reversed(mv))

    def get_beat_positions(self, note_id, time_passed):
        """
        Calculates led position for pulses on specified note
        :param note_id:  specified note id
        :return: pulse positions [list]
        """
        positions = []
        time_delta_ms = 0
        steps = (self.led_count) - 1
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
        Updates the array buffers, but does not send the buffer to Neopixel pin.
        :return: None
        """

        # clear previous buffer
        self.ws2812[:] = array('L', len(self.ws2812))
        self.ws2813[:] = array('L', len(self.ws2813))
        notes_anim = self.notes_anim

        for note_id, mv in self.notes_led.items():
            # load note animation
            anim = notes_anim[note_id]
            if anim:
                mv[:] = anim.color_array

            # led - note positions
            time_passed = self.game.time_passed()
            positions = self.get_beat_positions(note_id, time_passed)
            # if len(positions) > 0:
            #     print("POS", note_id, positions, time_expired)
            for pos in positions:
                if pos < 0 or pos > 33:
                    print("POS IS", pos)
                if note_id % 4 == 0:
                    mv[pos] = 0xACAC00
                elif note_id % 4 == 1:
                    mv[pos] = 0x00CF00
                elif note_id % 4 == 2:
                    mv[pos] = 0x0000CF
                elif note_id % 4 == 3:
                    mv[pos] = 0xAC00AC
            mv[-1] = 0xAFAFAF

        # load outer animation
        outer_anim = self.outer_anim
        for note_id, mv in self.outer_leds.items():
            anim = outer_anim[note_id]
            if anim:
                mv[:] = anim.color_array

    def tick_animation(self):
        anims = set(list(self.notes_anim.values()) + list(self.outer_anim.values()))
        [a.tick() for a in anims if a is not None]

    def clear_after_song(self):
        self.ws2813_np.clear()
        self.ws2812_np.clear()
        self.outer_np.clear()
        mp3_reset()
        time.sleep_ms(100)

    def clean_up(self):
        print("cleaning up..")
        mp3_reset()
        self.ws2813_np.clear()
        self.ws2812_np.clear()
        self.outer_np.clear()
        time.sleep_ms(500)
        # self.ws2813_np.deinit()
        # self.ws2812_np.deinit()
        # self.outer_np.deinit()

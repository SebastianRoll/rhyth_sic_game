import os
from rhyth_game_sync import RhythGame, SongFinished
from touch import Touch
import utime as time
import gc
import max7219
from machine import Pin, SPI

import pin_definitions as p


# spi = SPI(-1, baudrate=10000000, miso=Pin(pin_miso), mosi=Pin(pin_mosi), sck=Pin(pin_sck))
# display = max7219.Matrix8x8(spi, Pin(pin_slave_select_green), 4)
# display.text('1234', 0,0,1)
# display.show()
# display.fill(0)
# display.show()


# from machine import Neopixel, Pin
# np = Neopixel(Pin(pin_ws2813), 34*4)
# (T1H, T1L), (T0H, T0L), Treset = (580, 220), (220, 580), 280000  # WORKS PERFECTLY FOR WS2813!
# np.timings(((580, 220), (220, 580), 280000))
# np.set(0, 0xff0000, num=34*4)
# np2 = Neopixel(Pin(pin_ws2812), 34*4)
# np2.set(0, 0x00bb00, num=34*4)

# Available touch pins on ESP32:
# 0, 2 4, 12, 13, 14, 15, 27, 32, 33
# DAC: 25, 26



# r.notes_anim[1] = None
# r.notes_anim[0] = r.notes_anim[1]
# r.notes_anim[2] = r.notes_anim[1]
# r.notes_anim[3] = r.notes_anim[1]


class Menu:
    def __init__(self):

        self.delays = {
            'Bad Apple': 300,

        }

        self.song_list = {
            # 'Caramelldansen (Speedycake Remix)': 1,
            'Bad Apple': 3,
            # 'Elemental Creati': 3,
            'I know You know': 2,
            'boom_clap': 4,
            'Through the Fire and Flame': 1,
            'Southern Country 2': 7,
            # 'Eternal': 8,
            # 'Punjabi MC - Munda Tho Bach Ke Rahi': 9,
            # 'Salt N Peppa - Push It': 10,

        }
        t = Touch(p.touch_pins, threshold=150)

        self.r = RhythGame(p.pin_ws2812, p.pin_ws2813, p.pin_outer, touch_driver=t, brightness=255, song_list=self.song_list)


    def menu(self):
        r = self.r
        while True:
            gc.collect()
            songs = os.listdir('songs')
            print('SELECT SONG')
            song = self.select_option(songs)
            difficulties = os.listdir('songs/{}'.format(song))
            print('SELECT DIFFICULTY')
            difficulty = self.select_option(difficulties)
            self.play(song, difficulty)

    def play(self, song, difficulty, delay_ms=300):
        r = self.r
        try:
            r.play_song(delay_ms=delay_ms, title=song, difficulty=difficulty)
        except SongFinished:
            print("SCORE", r.game.points.score)
            return
        except Exception:
            r.clean_up()
            raise

    def select_option(self, options: list):
        next = self.contr_display.button_red_1.value
        prev = self.contr_display.button_red_2.value
        cur_idx = 0
        while True:
            n = not next()
            p = not prev()
            if n and p:
                return options[cur_idx]
            elif n:
                cur_idx += 1
            elif p:
                cur_idx -= 1
            print(options[cur_idx])
            time.sleep_ms(50)

# from animations.fire import Fire
menu = Menu()
# fire = Fire(34)
# menu.r.notes_anim[0] = fire
# menu.r.notes_anim[1] = fire
# menu.r.notes_anim[2] = fire
# menu.r.notes_anim[3] = fire
# menu.r.notes_anim[4] = fire
# menu.r.notes_anim[5] = fire
# menu.r.notes_anim[6] = fire
# menu.r.notes_anim[7] = fire
playlist = {
            'Through the Fire and Flame': 'Easy',
            # 'Caramelldansen (Speedycake Remix)': 'Easy',
            # 'boom_clap':'Challenge',
            # 'Elemental Creati':'Easy',
            # 'Salt N Peppa - Push It':'easy',
            # 'Punjabi MC - Munda Tho Bach Ke Rahi':'medium',
            # 'I know You know':'Hard',
            # 'Bad Apple':'Easy',
            # 'Southern Country 2':'Medium',
            # 'Eternal': 'Hard'
}
# while True:
for s, d in playlist.items():
    try:
        menu.play(song=s, difficulty=d, delay_ms=270)
        time.sleep_ms(15000)
    except KeyboardInterrupt:
        menu.r.clear_after_song()

# def main():
#     Menu()
#
# if __name__ == "__main__":
#     main()
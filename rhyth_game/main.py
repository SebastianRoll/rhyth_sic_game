import os
from machine import Pin, SPI
import max7219
from rhyth_game_sync import RhythGame, SongFinished
from touch import Touch
import utime as time
import gc

pin_mosi = 23
pin_miso = 19
pin_sck = 18
pin_slave_select_red = 17
pin_slave_select_green = 16
pin_button_red_1 = 35
pin_button_red_2 = 34
pin_uart2_rx = 32
pin_uart2_tx = 25
pin_ws2812 = 26
pin_ws2813 = 22
pin_outer = 5

# from machine import Neopixel, Pin
# np = Neopixel(Pin(26), 34*4)
# ((T1H, T1L), (T0H, T0L), Treset) = [(580, 220), (220, 580), 280000]  # WORKS PERFECTLY FOR WS2813!
# np.timings([(T1H, T1L), (T0H, T0L), Treset])
# np.set(0, 0xff0000, num=34*4)


touch_pins = [15, 33, 4, 13, 27, 12, 0, 2]
# r.notes_anim[1] = None
# r.notes_anim[0] = r.notes_anim[1]
# r.notes_anim[2] = r.notes_anim[1]
# r.notes_anim[3] = r.notes_anim[1]



class ControllerDisplay:
    def __init__(self):
        spi = SPI(1, baudrate=10000000, miso=Pin(pin_miso), mosi=Pin(pin_mosi), sck=Pin(pin_sck))
        self.display_red = max7219.Matrix8x8(spi, Pin(pin_slave_select_red), 4)
        self.display_green = max7219.Matrix8x8(spi, Pin(pin_slave_select_green), 4)
        self.button_red_1 = Pin(pin_button_red_1, Pin.PULL_UP)
        self.button_red_2 = Pin(pin_button_red_2, Pin.PULL_UP)


class Menu:
    def __init__(self):
        t = Touch(touch_pins, threshold=150)
        # self.contr_display = ControllerDisplay()
        self.r = RhythGame(pin_ws2812, pin_ws2813, pin_outer, touch_driver=t, brightness=1, debug=True, switch_led=False)
        self.r.play_song(delay_ms=400, title='boom_clap', difficulty='Challenge')

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
            try:
                r.play_song(delay_ms=400, title=song, difficulty=difficulty)
            except SongFinished:
                print("SCORE", r.game.points.score)
                continue
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


def main():
    Menu()

if __name__ == "__main__":
    main()
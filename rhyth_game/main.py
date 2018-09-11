pin_mosi = 23
pin_miso = 19
pin_sck = 18
pin_slave_select_red = 17
pin_slave_select_green = 16
pin_button_red = 35
pin_button_red = 34
pin_uart2_rx = 32
pin_uart2_tx = 25
pin_ws2812 = 26
pin_ws2813 = 22
pin_outer = 5

from rhyth_game_sync import RhythGame
from touch import Touch
# touch_pins = [4, 12, 13, 27, 33, 0, 2, 15]
touch_pins = [15, 33, 4, 13, 27, 12, 0, 2]
t = Touch(touch_pins, threshold=150)
r = RhythGame(pin_ws2812, pin_ws2813, pin_outer, touch_driver=t)
r.notes_anim[1] = None
r.notes_anim[0] = r.notes_anim[1]
r.notes_anim[2] = r.notes_anim[1]
r.notes_anim[3] = r.notes_anim[1]
# r.play_song(delay_ms=400, title='dr_chaos', difficulty='easy')
r.play_song(delay_ms=400, title='boom_clap', difficulty='Challenge')

## MAIN PROGRAM

pin_mosi = 23
pin_miso = 19
pin_sck = 18
pin_slave_select_red = 17
pin_slave_select_green = 16
pin_button_red = 35
pin_button_red = 34
pin_uart2_rx = 32
pin_uart2_tx = 25
pin_ws2812 = 26
pin_ws2813 = 22
pin_outer = 5






from machine import Neopixel, Pin
pin_ws2812 = 26
pin_ws2813 = 22
pin_outer = 5
np2 = Neopixel(Pin(pin_ws2812), 34*4)

# WS2813 timings: https://github.com/FastLED/FastLED/issues/449
# ((T1H,T1L), (T0H, T0L), Treset) = [(750, 300), (300, 300), 280000] # TRY!
# ((T1H,T1L), (T0H, T0L), Treset) = [(750, 300), (300, 300), 300000] # Works almost!
# ((T1H,T1L), (T0H, T0L), Treset) = [(750, 220), (200, 750), 300000]
# from machine import Neopixel, Pin
np2 = Neopixel(Pin(pin_ws2813), 34*4)
# print(np2.timings())
((T1H,T1L), (T0H, T0L), Treset) = [(580, 220), (220, 580), 280000] # WORKS PERFECTLY FOR WS2813!
np2.timings([(T1H,T1L), (T0H, T0L), Treset])
# np2 = Neopixel(Pin(pin_outer), 34*4, type=Neopixel.TYPE_RGBW) #5
# np2.set(50, 0x100000, num=50, update=False)
#
# class NeoPixel(Neopixel):
#     def set_buffer(self, buf):
#         # ar_ints = ustruct.unpack('>{}B'.format(34*4 * 3), buf)
#         # ar_leds = [ar_ints[r:r + 3] for r in range(0, len(ar_ints), 3)]
#         # print(ar_leds)
#         for led_pos in range(len(buf)//3):
#             rgb_buf = buf[led_pos*3:led_pos*3+3]
#             rgb_int = int.from_bytes(rgb_buf, 'big')
#             self.set(led_pos+1, rgb_int, update=False)
#         self.show()
#
# np2 = Neopixel(Pin(pin_ws2813), 34*4) #5
# # np2 = NeoPixel(Pin(pin_ws2813), 34*4) #5
# np = NeoPixel(Pin(pin_ws2812), 34*4) #5
# import utime
# def c(np, color=NeoPixel.RED):
#     np.set(0, color, num=34*4, update=False)
#     utime.sleep_ms(300)
#     np.show()


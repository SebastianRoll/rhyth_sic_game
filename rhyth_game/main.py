from machine import Neopixel, Pin

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
# np = Neopixel(Pin(pin_outer), 34*4)

from rhyth_game_sync import RhythGame
from touch import Touch
# touch_pins = [4, 12, 13, 27, 33, 0, 2, 15]
touch_pins = [15, 33, 4, 13, 27, 12, 0, 2]
t = Touch(touch_pins, threshold=150)
r = RhythGame(pin_ws2812, pin_ws2813, pin_outer, touch_driver=t, brightness=1, debug=True, switch_led=False)
# r.notes_anim[1] = None
# r.notes_anim[0] = r.notes_anim[1]
# r.notes_anim[2] = r.notes_anim[1]
# r.notes_anim[3] = r.notes_anim[1]
# r.play_song(delay_ms=400, title='dr_chaos', difficulty='easy')
try:
    r.play_song(delay_ms=400, title='boom_clap', difficulty='Challenge')
except:
    r.clean_up()
    raise

## MAIN PROGRAM

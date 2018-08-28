import uasyncio as asyncio
from machine import Pin
from asyn import Event
import neopixel
from asyn import Lock
from ledlights_async import NeopixelSlice, OuterRing
import random

from rhyth_game.button import touch
from rhyth_game.ledlights_async import refresh_leds, pulse_if_event

loop = asyncio.get_event_loop()

# outer = neopixel.NeoPixel(Pin(16), 220, bpp=4, timing=True)
# outer.fill([0,0,0,0])
# outer.write()
outer_top = OuterRing(outer, list(range(110)))
outer_bot = OuterRing(outer, list(range(219,110,-1)))


# loop.create_task(transition(outer, lock, 0, 0, 100, 0))

touch_pins = [12, 13, 27, 32, 33, 0, 2, 4]
note_pins = [17, 5, 19, 18]
touch_pins = [12, 13, 27, 32]
note_pins = [17, 5]
# touch_pins = [12, 13, 27, 32, 33, 0]
# note_pins = [17, 5, 19]

lock_outer = Lock()
loop.create_task(refresh_leds(outer, lock_outer))
loop.create_task(global_color_change())
loop.create_task(transition_circle(outer_top, degree=0))
for idx, _ in enumerate(touch_pins[::2]):
    lock = Lock()
    np = neopixel.NeoPixel(Pin(note_pins[idx]), 68, bpp=3, timing=True)
    np.fill([0,0,0])
    np.write()
    loop.create_task(refresh_leds(np, lock))
    touch_event_1 = Event()
    touch_event_2 = Event()
    loop.create_task(touch(touch_event_1, touch_pins[idx]))
    loop.create_task(touch(touch_event_2, touch_pins[idx + 1]))

    first = NeopixelSlice(np, list(range(34)))
    second = NeopixelSlice(np, list(range(67, 32, -1)))
    loop.create_task(pulse_if_event(first, touch_event_1))
    loop.create_task(pulse_if_event(second, touch_event_2))

loop.create_task(transition_circle(outer_bot, degree=1))

loop.run_forever()

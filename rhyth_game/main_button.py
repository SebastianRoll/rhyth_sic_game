import uasyncio as asyncio
from machine import Pin, TouchPad
from button import TouchPin, Pushbutton
from music import MusicMock
from uasyncio.queues import Queue

loop = asyncio.get_event_loop()
touch_pin = TouchPin(Pin(12))
touch_pin.config(600)

touch_button = Pushbutton(touch_pin)

def pressed():
    print("pressed!")

def pressed_queue(queue):
    result = "test"
    print("to queue")
    await queue.put(result)

def pressed_long():
    print("pressed long!")

queue = Queue()
touch_button.press_func(pressed_queue, (queue))
touch_button.long_func(pressed_long)

music = MusicMock()
loop.create_task(music.record(queue))

loop.run_forever()



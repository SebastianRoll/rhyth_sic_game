from machine import Pin, TouchPad
try:
    import utime as time
except ImportError:
    import time
from utils import timed_function

class Touch:
    def __init__(self, touch_pins, threshold=400):
        self.touchpads = [TouchPad(Pin(pin)) for pin in touch_pins]
        self.threshold = threshold
        self.cur_time = time.ticks_ms
        self.debounce_ms = 150

        cur_time = self.cur_time()
        self.ts_touches = [cur_time] * len(touch_pins)

    def cb(self):
        ts_touches = self.ts_touches
        threshold = self.threshold
        debounce_ms = self.debounce_ms

        is_touched = bytearray(len(ts_touches))

        ts = self.cur_time()
        try:
            for i, t in enumerate(self.touchpads):
                if t.read() < threshold and (ts - ts_touches[i]) > debounce_ms:
                    ts_touches[i] = ts
                    is_touched[i] = 1
                else:
                    pass
                    # istouch[i] = 0
            # return indices that are 1
            return [i for i,v in enumerate(is_touched) if v]
        except ValueError as e:
            print(e)
            raise


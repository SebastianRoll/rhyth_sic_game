from machine import Pin, TouchPad
try:
    import utime as time
except ImportError:
    import time
# from utils import timed_function

class Touch:
    def __init__(self, touch_pins, threshold=400):
        self.touchpads = [TouchPad(Pin(pin)) for pin in touch_pins]
        self.threshold = threshold
        # self.cur_time = time.ticks_ms
        self.debounce_ms = 75

        # cur_time = self.cur_time()
        self.was_touched = bytearray(len(touch_pins))
        # self.ts_touches = [cur_time] * len(touch_pins)

    # @timed_function
    def cb(self):
        # ts_touches = self.ts_touches
        threshold = self.threshold
        # debounce_ms = self.debounce_ms
        was_t = self.was_touched
        is_t = bytearray(len(was_t))
        # is_touched = []

        # ts = self.cur_time()
        v = False
        try:
            for i, t in enumerate(self.touchpads):
                v = t.read()
                v = v < threshold
                if v and was_t[i] == 0:#(ts - ts_touches[i]) > debounce_ms:
                    # ts_touches[i] = ts
                    is_t[i] = 1
                    was_t[i] = 1
                elif not v:
                    is_t[i] = 0
                    was_t[i] = 0
                    # istouch[i] = 0
            # return indices that are 1
            # return bytearray()
            return [i for i,v in enumerate(is_t) if v]
        except ValueError as e:
            print(e)
            raise

    def check_touch(self, i, update=True):
        t = self.touchpads[i]
        was_t = self.was_touched
        v = t.read()
        v = int(v < self.threshold)
        if update:
            if v and was_t[i] == 0:  # (ts - ts_touches[i]) > debounce_ms:
                # ts_touches[i] = ts
                was_t[i] = 1
            elif not v:
                was_t[i] = 0
        return v



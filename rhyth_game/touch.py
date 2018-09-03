from machine import Pin, TouchPad

class Touch:
    def __init__(self, touch_pins, threshold=400):
        self.touchpads = [TouchPad(Pin(pin)) for pin in touch_pins]
        self.threshold = threshold
        self.istouch = array(len(touch_pins))

    def cb(self):
        istouch = self.istouch
        threshold = self.threshold
        for i, t in enumerate(self.touchpads):
            if t.read() < threshold:
                istouch[i] = 1
            else:
                istouch[i] = 0

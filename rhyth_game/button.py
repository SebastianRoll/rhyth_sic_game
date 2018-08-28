from machine import TouchPad, Pin
import uasyncio as asyncio
import utime as time
from asyn import launch


async def touch_all(event, pins_no):
    touch_pins = []
    for pin_no in pins_no:
        touch_pin = TouchPad(Pin(pin_no))
        touch_pin.config(600)  # I think 0 is default sensitivity and higher is less sensitive
        touch_pins.append(touch_pin)
    while True:
        for touch_pin in touch_pins:
            if touch_pin.read() < 500:
                print("TOUCH {}".format(touch_pins.pin))
                event.set(touch_pins.pin)
        await asyncio.sleep(0.1)


async def touch(event, pin_no):
    touch_pin = TouchPad(Pin(pin_no))
    touch_pin.config(600)  # I think 0 is default sensitivity and higher is less sensitive
    # import ustruct
    # i2c = I2C(sda=Pin(23), scl=Pin(16))
    while True:
        while event.is_set():
            await asyncio.sleep(0.2)  # Wait for coro to respond
        if touch_pin.read() < 500:
            print("TOUCH {}".format(pin_no))
            event.set()
        # Acquire data from somewhere
        # style = bin(ustruct.unpack('>H', i2c.readfrom(87, 2))[0])
        # if int(style):
        #    event.set()

        await asyncio.sleep(0.05)


class TouchPin(TouchPad):
    THRESHOLD = 500

    def value(self):
        return self.read() < self.THRESHOLD


class Delay_ms(object):
    def __init__(self, func=None, args=(), can_alloc=True, duration=1000):
        self.func = func
        self.args = args
        self.can_alloc = can_alloc
        self.duration = duration  # Default duration
        self.tstop = None  # Not running
        self.loop = asyncio.get_event_loop()
        if not can_alloc:
            self.loop.create_task(self._run())

    async def _run(self):
        while True:
            if self.tstop is None:  # Not running
                await asyncio.sleep_ms(0)
            else:
                await self.killer()

    def stop(self):
        self.tstop = None

    def trigger(self, duration=0):  # Update end time
        if duration <= 0:
            duration = self.duration
        if self.can_alloc and self.tstop is None:  # No killer task is running
            self.tstop = time.ticks_add(time.ticks_ms(), duration)
            # Start a task which stops the delay after its period has elapsed
            self.loop.create_task(self.killer())
        self.tstop = time.ticks_add(time.ticks_ms(), duration)

    def running(self):
        return self.tstop is not None

    async def killer(self):
        twait = time.ticks_diff(self.tstop, time.ticks_ms())
        while twait > 0:  # Must loop here: might be retriggered
            await asyncio.sleep_ms(twait)
            if self.tstop is None:
                break  # Return if stop() called during wait
            twait = time.ticks_diff(self.tstop, time.ticks_ms())
        if self.tstop is not None and self.func is not None:
            launch(self.func, self.args)  # Timed out: execute callback
        self.tstop = None  # Not running


class Pushbutton(object):
    debounce_ms = 50
    long_press_ms = 1000
    double_click_ms = 400

    def __init__(self, pin):
        self.pin = pin  # Initialise for input
        self._true_func = False
        self._false_func = False
        self._double_func = False
        self._long_func = False
        self.sense = pin.value()  # Convert from electrical to logical value
        self.buttonstate = self.rawstate()  # Initial state
        loop = asyncio.get_event_loop()
        loop.create_task(self.buttoncheck())  # Thread runs forever

    def press_func(self, func, args=()):
        self._true_func = func
        self._true_args = args

    def release_func(self, func, args=()):
        self._false_func = func
        self._false_args = args

    def double_func(self, func, args=()):
        self._double_func = func
        self._double_args = args

    def long_func(self, func, args=()):
        self._long_func = func
        self._long_args = args

    # Current non-debounced logical button state: True == pressed
    def rawstate(self):
        return bool(self.pin.value() ^ self.sense)

    # Current debounced state of button (True == pressed)
    def __call__(self):
        return self.buttonstate

    async def buttoncheck(self):
        loop = asyncio.get_event_loop()
        if self._long_func:
            longdelay = Delay_ms(self._long_func, self._long_args)
        if self._double_func:
            doubledelay = Delay_ms()
        while True:
            state = self.rawstate()
            # State has changed: act on it now.
            if state != self.buttonstate:
                self.buttonstate = state
                if state:
                    # Button is pressed
                    if self._long_func and not longdelay.running():
                        # Start long press delay
                        longdelay.trigger(Pushbutton.long_press_ms)
                    if self._double_func:
                        if doubledelay.running():
                            launch(self._double_func, self._double_args)
                        else:
                            # First click: start doubleclick timer
                            doubledelay.trigger(Pushbutton.double_click_ms)
                    if self._true_func:
                        launch(self._true_func, self._true_args)
                else:
                    # Button release
                    if self._long_func and longdelay.running():
                        # Avoid interpreting a second click as a long push
                        longdelay.stop()
                    if self._false_func:
                        launch(self._false_func, self._false_args)
            # Ignore state changes until switch has settled
            await asyncio.sleep_ms(Pushbutton.debounce_ms)

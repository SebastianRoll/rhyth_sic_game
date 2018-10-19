"""
ESP32 SPI peripheral can be used with any GPIO via GPIO matrix (input only GPIOS can be used only for miso function).

Native SPI pins are (clk, mosi, miso, cs):
SPI1: 6, 8, 7, 11
HSPI: 14,13,12,15
VSPI: 18,23,19, 5
If using native pins maximum SPI clock can be set to 80 MHZ.
If using the pins routed via gpio matrix, maximum spi clock is 40 MHz in half-duplex mode and 26 MHz in full duplex mode.

Only HSPI & VSPI are supported by esp-idf driver.
Additionally, if psRAM is used with ESP32, and is set to run at 80MHz, VSPI is not available to the user, as it is used by psRAM driver.

So, in most cases (if you don't need the speed >26 MHz), you can use any pin for miso and any input/output pin for mosi, clk & cs.
"""

import display
from machine import Pin, SPI
import time

import max7219
from encoder import Encoder

import pin_definitions as pd

class TFT(display.TFT):
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exit")


class RhythBox:
    def __init__(self):
        self.tft = None
        self.spi = None

        self.button_left = Pin(pd.PIN_BUTTON_LEFT, Pin.IN, Pin.PULL_UP)
        self.button_right = Pin(pd.PIN_BUTTON_RIGHT, Pin.IN, Pin.PULL_UP,
                                handler=self.button_pressed, trigger=Pin.IRQ_FALLING)#, debounce=10000, acttime=5000)

        self.encoder_left = Encoder(pd.PIN_ENCODER_LEFT_SCK, pd.PIN_ENCODER_LEFT_DT, min_val=0, clicks=2)
        self.encoder_right = Encoder(pd.PIN_ENCODER_RIGHT_SCK, pd.PIN_ENCODER_RIGHT_DT, min_val=0, clicks=2)


        self.numval = 0
        self.debounce_ms = 50
        self.butr_debounce = 0

        self.switch_matrix()
        self.switch_tft()

    def button_pressed(self, pin):
        if time.ticks_ms() > self.butr_debounce and pin.value() == 0:
            self.numval += 1
            # print(pin.value())
            self.butr_debounce = time.ticks_add(time.ticks_ms(), self.debounce_ms)
        # irq_state = machine.disable_irq()
        # print(pin.value())
        # machine.enable_irq(irq_state)

    def show_image(self, path='01.jpg', text=""):
        self.switch_tft()
        tft = self.tft
        tft.clear(0x000000)
        tft.image(tft.CENTER, tft.CENTER, path)
        if text:
            tft.text(tft.CENTER, 2, text, tft.CYAN, transparent=True)

    def switch_tft(self):
        if self.spi:
            self.led_right.fill(0)
            self.led_right.show()
            self.led_right.fill(0)
            self.led_right.show()
            self.spi.deinit()
            self.spi = None

        if not self.tft:
            tft = display.TFT()
            tft.init(tft.ILI9341, width=240, height=320, miso=pd.PIN_MISO, mosi=pd.PIN_MOSI, clk=pd.PIN_SCK,
                     cs=pd.PIN_TFT_CS, dc=pd.PIN_TFT_DC, rst_pin=pd.PIN_TFT_RST, bgr=True)
            tft.rect(0, 20, 100, 100, 0xFF0000, 0x00FF00)
            self.tft = tft

    def switch_matrix(self):
        if self.tft:
            self.tft.deinit()
            self.tft = 0

        if not self.spi:
            spi = SPI(spihost=1, baudrate=8000000, miso=Pin(pd.PIN_MISO), mosi=Pin(pd.PIN_MOSI), sck=Pin(pd.PIN_SCK))
            led_right = max7219.Matrix8x8(spi, Pin(pd.PIN_8X8_1_CS), 4)
            led_right.brightness(2)
            led_right.fill(0)
            led_right.show()

            led_left = max7219.Matrix8x8(spi, Pin(pd.PIN_8X8_2_CS), 4)
            led_left.brightness(2)
            led_left.fill(0)
            led_left.show()

            self.spi = spi
            self.led_right = led_right
            self.led_left = led_left

    def close(self):
        self.encoder_left.close()
        self.encoder_right.close()


if __name__ == "__main__":
    box = RhythBox()

    box.switch_matrix()
    while True:
        box.led_right.fill(0)
        box.led_right.text(str(box.numval), 0, 0, 1)
        box.led_right.show()

        box.led_left.fill(0)
        box.led_left.text(str(box.button_right.value()), 0, 0, 1)
        box.led_left.show()
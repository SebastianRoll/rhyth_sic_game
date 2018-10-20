Diameter without rim = 63 cm
36 pixels per note = 25.2 cm
diameter inner circle = 12.6 cm

ca 24 pixles inner circle

Led strip width: 1.24 cm

https://learn.adafruit.com/sipping-power-with-neopixels

5V power supply below diagonally shifter bajs



NEW

Diameter without rim = 60 cm
34 pixels per note = 24.7 cm
diameter inner circle = 12.6 cm


TODO:

* test cmath
* test FancyLED
* test main_button.py
* test led_patterns.py
* touch IRS (sets flag)
* put fast_io on ESP32
* meteor effect on [_SUPERCOMBO_](https://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/#MakeyoureffectscoolerDiffuseLighttoiletpapermagic)
* Issue with all note nps:
```
PYB: soft reboot
OSError: [Errno 2] ENOENT
Traceback (most recent call last):
  File "main.py", line 125, in <module>
  File "/lib/uasyncio/core.py", line 42, in create_task
  File "/lib/uasyncio/core.py", line 57, in call_later_ms
  File "/lib/uasyncio/core.py", line 48, in call_soon
IndexError: full
```

## NeoPixel

NeoPixels receive data from a fixed-frequency 800 KHz datastream (except for “V1” Flora pixels, which use 400 KHz). Each bit of data therefore requires 1/800,000 sec — 1.25 microseconds. One pixel requires 24 bits (8 bits each for red, green blue) — 30 microseconds. After the last pixel’s worth of data is issued, the stream must stop for at least 50 microseconds for the new colors to “latch.”

For a strip of 100 pixels, that’s (100 * 30) + 50, or 3,050 microseconds. 1,000,000 / 3,050 = 328 updates per second, approximately.

220 rgbw = 220*(8*4) = 7040
280 rgb = 280*(8*3) = 6720

total = 7040 + 6720 + 50 = 13810 us = 13.81 ms -> 72.4 Hz

# NP.WRITE()

2.5 ms for 68 rgb leds
9.5 ms for 220 grbw leds


# Convert song
`python smdataset.py "/home/sebastian/Music/StepMania/GOOD/packs/1 o' KLOC/Boom Clap Aeroplane remix" res`



# TODO

Scoreboard

2 led matrix displays
Player select

glue broken pad

TEST SYSTEM

paint leds white

## Software

- main
  - select song
- mp3
  - play_track(10)
- performance
  - song read
- Scoreboard class
  - lifebar
- songs

- choice between easy and medium
- fix double-tap issue!
- change beat offset
- change timing start
## Debugging

- one note led wire (ws2812, V++) broke apart at solder joint
- brightness=1 caused yellow and pink to not show at all

ISpindel - hygrometer


## Performance
Function set_buffer Time = 35.622ms
Function cb Time = 32.337ms
Function refresh_outer_leds Time =  0.817ms


## ESP32

### Input only pins
GPIOs 34 to 39 are GPIs – input only pins. These pins don’t have internal pull-ups or pull-down resistors. They can’t be used as outputs, so use these pins only as inputs:

- GPIO 34
- GPIO 35
- GPIO 36
- GPIO 37
- GPIO 38
- GPIO 39

### SPI flash integrated on the ESP-WROOM-32

GPIO 6 to GPIO 11 are exposed in some ESP32 development boards. However, these pins are connected to the integrated SPI flash on the ESP-WROOM-32 chip and are not recommended for other uses. So, don’t use these pins in your projects:

- GPIO 6 (SCK/CLK)
- GPIO 7 (SDO/SD0)
- GPIO 8 (SDI/SD1)
- GPIO 9 (SHD/SD2)
- GPIO 10 (SWP/SD3)
- GPIO 11 (CSC/CMD)

### Capacitive touch GPIOs


- T0 (GPIO 4)
- T1 (GPIO 0)
- T2 (GPIO 2)
- T3 (GPIO 15)
- T4 (GPIO 13)
- T5 (GPIO 12)
- T6 (GPIO 14)
- T7 (GPIO 27)
- T8 (GPIO 33)
- T9 (GPIO 32)

### Analog to Digital Converter (ADC)

The ESP32 has 18 x 12 bits ADC input channels (while the ESP8266 only has 1x 10 bits ADC). These are the GPIOs that can be used as ADC and respective channels:

- ADC1_CH0 (GPIO 36)
- ADC1_CH1 (GPIO 37)
- ADC1_CH2 (GPIO 38)
- ADC1_CH3 (GPIO 39)
- ADC1_CH4 (GPIO 32)
- ADC1_CH5 (GPIO 33)
- ADC1_CH6 (GPIO 34)
- ADC1_CH7 (GPIO 35)
- ADC2_CH0 (GPIO 4)
- ADC2_CH1 (GPIO 0)
- ADC2_CH2 (GPIO 2)
- ADC2_CH3 (GPIO 15)
- ADC2_CH4 (GPIO 13)
- ADC2_CH5 (GPIO 12)
- ADC2_CH6 (GPIO 14)
- ADC2_CH7 (GPIO 27)
- ADC2_CH8 (GPIO 25)
- ADC2_CH9 (GPIO 26)

### Digital to Analog Converter (DAC)
There are 2 x 8 bits DAC channels on the ESP32 to convert digital signals into analog voltage signal outputs. These are the DAC channels:

- DAC1 (GPIO25)
- DAC2 (GPIO26)

GPIO current drawn
The absolute maximum current drawn per GPIO is 40mA according to the “Recommended Operating Conditions” section in the ESP32 datasheet.
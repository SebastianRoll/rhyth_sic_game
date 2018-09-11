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


# DEMO

# Mapping scoreboard (esp32 to scoreboard)

14 lilla lilla
5v grå rød
G hvit hvit
5 grønn hvit
23 gul(uten tape) grønn
26 gul(med tape) svart
17 grønn lilla
16 blå blå
18 brun grå

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
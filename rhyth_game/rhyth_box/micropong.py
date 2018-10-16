"""
µPong game by Pål Grønås Drange
https://github.com/Statoil/micropython/wiki/A-game-of-Pong
"""

from machine import Pin

# LED
# MOSI = Pin(13)  # master out slave in
# SCK  = Pin(9)  # clock
# CS   = Pin(5)  # cable select

# CAPACITIVE
# SDA = Pin(33)
# SCL = Pin(23)
# i2c = I2C(sda=SDA, scl=SCL)
# µPong
import math
import time
from random import randint
from cmath import exp, pi
import ustruct
from machine import Pin, SPI, ADC, I2C

import max7219
from pin_definitions import *

### 8x8 MATRIX
MISO = Pin(PIN_MISO)  # not in use -- master in slave out
MOSI = Pin(PIN_MOSI)  # master out slave in
SCK  = Pin(PIN_SCK)  # clock
CS   = Pin(PIN_8X8_1_CS)  # cable select

spi  = SPI(spihost=1, baudrate=8000000, miso=MISO, mosi=MOSI, sck=SCK)
display = max7219.Matrix8x8(spi, CS, 4)
display.brightness(10)
display.fill(0)
display.show()

def show_board(game):
    display.fill(0)

    display.pixel(0, game.left_pad-1, 1)
    display.pixel(0, game.left_pad, 1)
    display.pixel(0, game.left_pad+1, 1)

    display.pixel(31, game.right_pad-1, 1)
    display.pixel(31, game.right_pad, 1)
    display.pixel(31, game.right_pad+1, 1)

    ball = int(round(game.ball[0])), int(round(game.ball[1]))
    display.pixel(ball[0], ball[1], 1)
    display.show()

def show_ball(game):
    ball = int(round(game.ball[0])), int(round(game.ball[1]))
    for i in range(10):
        display.pixel(ball[0], ball[1], (i%2)==0)
        display.show()
        time.sleep(0.1)

def show_score(game):
    a,b = game.the_score
    x_idx = 4
    if max(a,b) > 9:
        x_idx = 0
    for i in range(5):
        display.brightness(i)
        display.fill(0)
        display.show()
        time.sleep(0.1)
        display.text('{}:{}'.format(a,b), x_idx, 0, 1)
        display.show()
        time.sleep(0.2)
    display.fill(0)
    display.show()

def countdown():
    for i in range(10, -1, -1):
        display.fill(0)
        display.text('{}'.format(i), 10, 0, 1)
        display.show()
        time.sleep(0.2)
### END 8x8 MATRIX



### CAPACITIVE
# SDA = Pin(33)
# SCL = Pin(23)
# i2c = I2C(sda=SDA, scl=SCL)
#
# def human_pad():
#     """Return [0,7] or None"""
#     touch_array = ustruct.unpack('>H', i2c.readfrom(87,2))[0]
#     for i in range(15):
#         if touch_array & (1<<i):
#             return i//2
#     return None
### END CAPACITATIVE

class SnakePosition:
    def __init__(self):
        self.button_up = Pin(PIN_BUTTON_LEFT, Pin.IN, Pin.PULL_UP)
        self.button_down= Pin(PIN_BUTTON_RIGHT, Pin.IN, Pin.PULL_UP)
        self.numval = 0
        self.debounce_ms = 20
        self.pos_debounce = 0
        self.position = 4

    def update_position(self):
        if time.ticks_ms() > self.pos_debounce:
            # print(self.button_up.value(), self.button_down.value(), self.position)
            self.pos_debounce = time.ticks_add(time.ticks_ms(), self.debounce_ms)
            if self.button_up.value() == 0 and self.button_down.value() == 0:
                return self.position
            elif self.button_up.value() == 0 and self.position < 6:
                self.position += 1
            elif self.button_down.value() == 0 and self.position > 1:
                self.position -= 1
        return self.position

### START GAME
class Pong(object):
    def __init__(self):
        self.left_pad = 4
        self.right_pad = 4
        self.ball = [0,0]
        self.vector = [0,0]
        self.the_score = [0,0]
        self.snakepos = SnakePosition()
        self._start()

    def _start(self):
        self.ball = [16,4]
        self.vector = [1.0, 0.2]
        if randint(0,1):
            self.vector[0] = -self.vector[0]
        if randint(0,1):
            self.vector[1] = -self.vector[1]

    def _is_goal(self):
        if self.ball[0] <= 0:
            self.ball[0] = 0
            return -1
        if self.ball[0] >= 31:
            self.ball[0] = 31
            return 1
        return 0  # no goal == 0

    def _score(self):
        goal = self._is_goal()
        if goal != 0:
            goal += 1
            goal = goal//2
            self.the_score[1-goal] += 1
            show_ball(self)
            show_score(self)
            self._start()

    def _edge_of_bat(self):
        ball = int(round(self.ball[0])), int(round(self.ball[1]))
        if ball[0] == 1 and ball[1] == self.left_pad - 1:
            self.vector[1] = -abs(self.vector[1])*1.2
        elif ball[0] == 1 and ball[1] == self.left_pad + 1:
            self.vector[1] =  abs(self.vector[1])*1.2
        elif ball[0] == 30 and ball[1] == self.right_pad - 1:
            self.vector[1] = -abs(self.vector[1])*1.2
        elif ball[0] == 30 and ball[1] == self.right_pad + 1:
            self.vector[1] =  abs(self.vector[1])*1.2

    def _collision_detection(self):
        if self.ball[0] <= 1 and abs(self.ball[1] - self.left_pad) < 2:
            self.ball[0] = 1
            self.vector[0] = -self.vector[0]
            self._inc_speed()
            self._edge_of_bat()
        elif self.ball[0] >= 30 and abs(self.ball[1] - self.right_pad) < 2:
            self.ball[0] = 30
            self.vector[0] = -self.vector[0]
            self._inc_speed()
            self._edge_of_bat()

        if self.ball[1] < 0:
            self.vector[1] = -self.vector[1]
            self.ball[1] = 0
        elif self.ball[1] > 7:
            self.vector[1] = -self.vector[1]
            self.ball[1] = 7


    def _inc_speed(self):
        self.vector[0] *= 1.1

    def _ai(self):
        if int(self.ball[0]) % 2 == 0:  # easy/medium/hard = 4/3/2
            if self.right_pad > self.ball[1] + 2:
                self.right_pad -= 1
            elif self.right_pad < self.ball[1] - 2:
                self.right_pad += 1
        else:
            self.right_pad = min(6, max(self.right_pad + randint(-1,1), 1))

        self.left_pad = self.snakepos.update_position()
        # if y is not None:
        #     self.left_pad = y

    def update(self):
        self._ai()
        self.ball[0] += self.vector[0]
        self.ball[1] += self.vector[1]
        self._collision_detection()
        self._score()
        return self.left_pad, self.right_pad, self.ball, self.vector

    def __repr__(self):
        return 'Pong({}\t{}\t{}\t{})'.format(self.left_pad, self.right_pad, self.ball, self.vector)


def play():
    game = Pong()
    while max(game.the_score) < 10:
        game.update()
        show_board(game)
        time.sleep(0.05)

countdown()
show_board(Pong())
time.sleep(0.5)
play()
import neopixel
import time
import machine


def demo_clear(np):
    n = np.n
    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

def demo(np):
	n = np.n
	# cycle
	for i in range(4 * n):
	    for j in range(n):
	        np[j] = (0, 0, 0)
	    np[i % n] = (255, 255, 255)
	    np.write()
	    time.sleep_ms(25)
	demo_clear(np)

def demo_bounce(np):
    n = np.n

    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)
	demo_clear(np)

def demo_fade(np):
    n = np.n
    # fade in/out
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()
    demo_clear(np)


from machine import Pin, I2C
import ustruct
import math
delay = 2
n = 220
np = neopixel.NeoPixel(machine.Pin(17), n, bpp=4, timing=True)
import neopixel
import time
import random

def t():
	i2c = I2C(sda=Pin(23), scl=Pin(16))
	style = bin(ustruct.unpack('>H', i2c.readfrom(87,2))[0])
	if int(style):
		return True
	else:
		return False

def lights(fra, til):
	n = til
	a = random.randint(0,255)
	b = random.randint(0,255)
	colors = [[255,a,b,0],[a,255,b,0],[a,b,255,0]]
	color = colors[random.randint(0,2)]
	#color = [random.randint(10, 140) for i in range(3)]
	#color[random.randint(0,2)] = 0
	#print(color)
	for i in range(fra, til):
		np[n-(i+1)] = color
		np[i] = color
		if i > 1:
			np[n-(i+1)+1] = (0,0,0,0)
			np[i-1] = [int(c/2) for c in color]
			np[i-2] = [int(c/4) for c in color]
			np[i-3] = [int(c/8) for c in color]
			np[i-4] = [int(c/16) for c in color]
			np[i-5] = (0, 0, 0,0)
			#if i%1 == 0:
			#	np[i-6] = [random.randint(0, 2) for i in range(3)]
		time.sleep_ms(delay)
		np.write()
		while True:
			if t():
				print("go!")
				break 
			print("no!")

from machine import Pin, I2C
import ustruct
import math


def itouch(fra, til):
	while True:
		lights(fra, til)


#from machine import Pin, PWM
#p = Pin(17, Pin.PULL_UP)
#s = PWM(Pin(17), duty=1, freq=100)
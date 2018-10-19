import max7219
import uasyncio
from machine import Pin, SPI, PWM

async def temp():
    import dht
    from time import sleep

    d = dht.DHT22(Pin(4))
    while True:
        print('measuring..')
        d.measure()
        # await uasyncio.sleep_ms(200)
        t = d.temperature()
        h = d.humidity()
        display.fill(0)
        display.text('{}C'.format(int(t)), 0, 0, 1)
        display.show()
        buz_ch1.duty(0)
        sleep(1)
        await uasyncio.sleep(5)


async def killer(seconds=10):
    print("sleeping {} seconds".format(seconds))
    await uasyncio.sleep(seconds)


loop = uasyncio.get_event_loop()
loop.create_task(temp())

try:
    loop.run_until_complete(killer())
finally:
    pass

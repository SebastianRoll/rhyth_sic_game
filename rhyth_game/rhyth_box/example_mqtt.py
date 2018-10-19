import network
import utime

wifi('ZanderK-Guest', 'zanderk2017')

def conncb(task):
    print("[{}] Connected".format(task))

def disconncb(task):
    print("[{}] Disconnected".format(task))

def subscb(task):
    print("[{}] Subscribed".format(task))

def pubcb(pub):
    print("[{}] Published: {}".format(pub[0], pub[1]))

def datacb(msg):
    print("[{}] Data arrived from topic: {}, Message:\n".format(msg[0], msg[1]), msg[2])


mqtt = network.mqtt("mosq-pub", "mqtt://test.mosquitto.org", cleansession=True, connected_cb=conncb, disconnected_cb=disconncb, subscribed_cb=subscb, published_cb=pubcb, data_cb=datacb)
# secure connection requires more memory and may not work
# mqtts = network.mqtt("eclipse", "mqtts//iot.eclipse.org", cleansession=True, connected_cb=conncb, disconnected_cb=disconncb, subscribed_cb=subscb, published_cb=pubcb, data_cb=datacb)
# wsmqtt = network.mqtt("eclipse", "ws://iot.eclipse.org:80/ws", cleansession=True, data_cb=datacb)

mqtt.start()

tmo = 0
while mqtt.status()[0] != 2:
    utime.sleep_ms(100)
    tmo += 1
    if tmo > 80:
        print("Not connected")
        break

mqtt.subscribe('test')
mqtt.publish('test', 'Hi from Micropython')

mqtt.stop()
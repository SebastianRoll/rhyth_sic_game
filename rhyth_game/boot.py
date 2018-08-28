import network

sta_if = network.WLAN(network.STA_IF)
print('connecting to network...')
sta_if.active(True)
sta_if.connect('Work-Work by ITsjefen', '')
while not sta_if.isconnected():
    pass
print('network config:', sta_if.ifconfig())

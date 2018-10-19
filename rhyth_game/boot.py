# connect to a WIFI AP, sync time and start telnet and FTP server
# Paste it in the Python command line (REPL)
# Then you can connect to the IP of your ESP32 in FTP (passive mode) or in telnet !

wifi_ssid = "HackheimWifi"
wifi_passwd = "TeletextFTW"

import network
import utime
import machine
import gc
import os


def wifi(ssid="HackheimWifi", pwd="TeletextFTW"):
    sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
    sta_if.connect(ssid, pwd)

    tmo = 50
    while not sta_if.isconnected():
        utime.sleep_ms(100)
        tmo -= 1
        if tmo == 0:
            break
    if tmo > 0:
        ifcfg = sta_if.ifconfig()
        print("WiFi started, IP:", ifcfg[0])
        utime.sleep_ms(500)

        rtc = machine.RTC()
        print("Synchronize time from NTP server ...")
        rtc.ntp_sync(server="hr.pool.ntp.org")
        tmo = 100
        while not rtc.synced():
            utime.sleep_ms(100)
            tmo -= 1
            if tmo == 0:
                break

        if tmo > 0:
            utime.sleep_ms(200)
            print("Time set:", utime.strftime("%c"))
            print("")


def ftp(user="micro", password="python"):
    network.ftp.start(user=user, password=password, buffsize=1024, timeout=300)


def telnet():
    network.telnet.start(user="micro", password="python", timeout=300)


def df():
  s = os.statvfs('')
  return ('{0} MB'.format((s[0]*s[3])/1048576))


def free(full=False):
  gc.collect()
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}%'.format(F/T*100)
  if not full: return P
  else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))
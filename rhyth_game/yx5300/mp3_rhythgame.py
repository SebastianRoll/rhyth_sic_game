import yx5300 as cmd
from machine import UART


class MP3:
    def __init__(self, volume_level=15):
        self.uart = UART(2, baudrate=9600, rx=25, tx=32, timeout=10)
        self.volume_level = volume_level

    def play_track(self, track_id):
        self.uart.write(cmd.play_track(track_id))

    def set_volume(self, level):
        self.volume_level = level
        self.uart.write(cmd.set_volume(level))

import time
import board
import busio
from adafruit_ht16k33 import segments
from timerController import TickListener
class IDisplayController(TickListener):
    def killDisplay(self):
        raise NotImplementedError
    def enableDisplay(self):
        raise NotImplementedError
    def setSeconds(self, seconds):
        raise NotImplementedError
    def setDisplayMode(self, mode):
        raise NotImplementedError
    def onTick(self, seconds, countingDown):
        self.setSeconds(seconds)
class AF_HT16K33_7Seg(IDisplayController):
    MODE_MMSS = 0
    def __init__(self, i2c):
        self.i2c = i2c
        self.display = segments.Seg7x4(i2c)
        self.mode = AF_HT16K33_7Seg.MODE_MMSS
    def killDisplay(self):
        pass
    def enableDisplay(self):
        pass
    def setSeconds(self, totalSeconds):
        if(self.mode == AF_HT16K33_7Seg.MODE_MMSS):
            minutes = totalSeconds // 60
            seconds = totalSeconds - minutes * 60
            stringToDisplay = str(minutes%100) + ':' + str(seconds)
            print('\r'+str,end='')
            self.display.print(stringToDisplay)
    def setDisplayMode(self, mode):
        self.mode = mode


import time
import board
import busio
from adafruit_ht16k33 import segments
from timerController import TickListener
from roomController import RoomEvent
class IDisplayController(TickListener):
    def killDisplay(self):
        raise NotImplementedError
    def enableDisplay(self):
        raise NotImplementedError
    def setSeconds(self, seconds):
        raise NotImplementedError
    def onTick(self, seconds, countingDown):
        raise NotImplementedError
class AF_HT16K33_7Seg(IDisplayController):
    MODE_MMSS = 0
    def __init__(self, i2c):
        self.i2c = i2c
        self.display = segments.Seg7x4(i2c)
        self.mode = AF_HT16K33_7Seg.MODE_MMSS
        self.blink = False
    def killDisplay(self):
        pass
    def enableDisplay(self):
        pass
    def setSeconds(self, totalSeconds):
        if(totalSeconds > 0):
            minutes = totalSeconds // 60
            seconds = totalSeconds - minutes * 60
            stringToDisplay = ( '%02d' % (minutes%100) ) + ':' + ( '%02d' % (seconds) )
            print('\r'+stringToDisplay,end='')
            self.display.print(stringToDisplay)
            self.blink = True
            self.display.blink_rate = 2
        else:
            self.display.print('00:00')
            self.blink = False
            self.display.blink_rate = 0
    def setDisplayMode(self, mode):
        self.mode = mode
    def onTick(self, seconds, countingDown):
        self.setSeconds(seconds)
class CommandLineDisplay(IDisplayController):
    def killDisplay(self):
        pass
    def enableDisplay(self):
        pass
    def setSeconds(self, totalSeconds):
        minutes = totalSeconds // 60
        seconds = totalSeconds - minutes * 60
        stringToDisplay = ( '%02d' % (minutes%100) ) + ':' + ( '%02d' % (seconds) )
        print('\r'+stringToDisplay,end='')
    def setDisplayMode(self, mode):
        pass
    def onTick(self, seconds, countingDown):
        self.setSeconds(seconds)

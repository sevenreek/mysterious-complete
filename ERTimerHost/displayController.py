import time
import board
import busio
from adafruit_ht16k33 import segments
from timerController import TickListener, TimerEventListener, TimerEvent
class IDisplayController(TickListener, TimerEventListener):
    def killDisplay(self):
        raise NotImplementedError
    def enableDisplay(self):
        raise NotImplementedError
    def setSeconds(self, seconds):
        raise NotImplementedError
    def setDisplayMode(self, mode):
        raise NotImplementedError
    def onTick(self, seconds, countingDown):
        raise NotImplementedError
        
    def onEvent(self, event):
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
        if(self.mode == AF_HT16K33_7Seg.MODE_MMSS):
            if(totalSeconds > 0):
                minutes = totalSeconds // 60
                seconds = totalSeconds - minutes * 60
                stringToDisplay = ( '%02d' % (minutes%100) ) + ':' + ( '%02d' % (seconds) )
                print('\r'+stringToDisplay,end='')
                self.display.print(stringToDisplay)
            else:
                self.display.print('00:00')
                
    def setDisplayMode(self, mode):
        self.mode = mode
    def onTick(self, seconds, countingDown):
        self.setSeconds(seconds)
    def onEvent(self, event):
        if(event.type == TimerEvent.EVENT_RESUME or event.type == TimerEvent.EVENT_PAUSE):
            self.setSeconds(event.data[0])
        elif(event.type == TimerEvent.EVENT_HITZERO):
            self.blink = True
            self.display.blink_rate = 2
            print("Hit zero event")
        elif(event.type == TimerEvent.EVENT_TIMECHANGED):
            if(event.data[0]>0):
                self.blink = False
                self.display.blink_rate = 0

import time
from BaseRoomController import BaseRoomController
from GameEvents import GameEvent, BaseGameEvents
from TimerListeners import TickObserver

class UpdateListener():
    def update(self):
        raise NotImplementedError

class UnthreadedTimer(UpdateListener):
    def __init__(self):
        self.tickListeners = []
        self.secondsRemaining = 0
        self.countingDown = False
        self.lastTick = 0
    def update(self):
        if(self.countingDown):
            tickVal = time.time()
            if( ( tickVal-self.lastTick ) >= 1 ):
                self.secondsRemaining = ( self.secondsRemaining - int(tickVal-self.lastTick) )
                self.onTick()
                self.lastTick = tickVal
    def setStart(self, withValue = 0):
        self.secondsRemaining = withValue
        self.resume()
    def pause(self):
        self.countingDown = False
    def resume(self):
        self.lastTick = time.time()
        if(self.secondsRemaining>0):
            self.countingDown = True
    def setSeconds(self, value):
        self.secondsRemaining = value
        self.onTick()
    def getStatus(self):
        return (self.secondsRemaining, self.countingDown)
    def addSeconds(self, value):
        self.setSeconds(self.secondsRemaining + value)
    def appendTickListener(self, listener:TickObserver):
        self.tickListeners.append(listener)
    def onTick(self):
        for listener in self.tickListeners:
            listener.onTick(self.secondsRemaining, self.countingDown)



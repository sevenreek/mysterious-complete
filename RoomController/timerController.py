import time
from BaseRoomController import BaseRoomController, GameEvent, BaseGameEvents
#test

class UpdateListener():
    def onUpdate(self):
        raise NotImplementedError
class TickListener():
    def onTick(self, secLeft, countingDown):
        raise NotImplementedError
class UnthreadedTimer(UpdateListener):
    def __init__(self, roomController : BaseRoomController):
        self.tickListeners = []
        self.secondsRemaining = 0
        self.countingDown = False
        self.lastTick = 0
        self.roomctrl = roomController
    def onUpdate(self):
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
    def appendTickListener(self, listener):
        self.tickListeners.append(listener)
    def onTick(self):
        for listener in self.tickListeners:
            listener.onTick(self.secondsRemaining, self.countingDown)
        if(self.secondsRemaining == 0 and self.countingDown):
            self.pause()
            self.roomctrl.raiseEvent(GameEvent(BaseGameEvents.TIMER_HITZERO, None))

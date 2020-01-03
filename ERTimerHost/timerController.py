import time
class UpdateListener():
    def onUpdate(self):
        raise NotImplementedError
class TimerSubscriberSocket():
    def getStatus(self):
        raise NotImplementedError
class TickListener():
    def onTick(self, secLeft, countingDown):
        raise NotImplementedError
class TimerEvent():
    EVENT_NONE = 0
    EVENT_RESUME = 1
    EVENT_PAUSE = 2
    EVENT_HITZERO = 3
    EVENT_TIMECHANGED = 4
    def __init__(self, etype, data):
        self.type = etype
        self.data = data
class TimerEventListener():
    def onEvent(self, event):
        raise NotImplementedError
class UnthreadedTimer(UpdateListener):
    def __init__(self):
        self.tickListeners = []
        self.eventListeners = []
        self.secondsRemaining = 0
        self.countingDown = False
        self.lastTick = 0
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
        self.raiseEvent(TimerEvent(TimerEvent.EVENT_PAUSE,self.secondsRemaining))
    def resume(self):
        self.lastTick = time.time()
        self.countingDown = True
        self.raiseEvent(TimerEvent(TimerEvent.EVENT_RESUME,self.secondsRemaining))
    def setSeconds(self, value):
        self.secondsRemaining = value
        self.raiseEvent(TimerEvent(TimerEvent.EVENT_TIMECHANGED, self.secondsRemaining))
    def getStatus(self):
        return (self.secondsRemaining, self.countingDown)
    def addSeconds(self, value):
        self.secondsRemaining = self.secondsRemaining + value
        self.raiseEvent(TimerEvent(TimerEvent.EVENT_TIMECHANGED, self.secondsRemaining))
    def appendTickListener(self, listener):
        self.tickListeners.append(listener)
    def appendEventListener(self, listener):
        self.eventListeners.append(listener)
    def raiseEvent(self, event):
        for listener in self.eventListeners:
            listener.onEvent(event)
    def onTick(self):
        for listener in self.tickListeners:
            listener.onTick(self.secondsRemaining, self.countingDown)
        if(self.secondsRemaining == 0 and self.countingDown):
            self.pause()
            self.raiseEvent(TimerEvent(TimerEvent.EVENT_HITZERO,None))

import time
class UpdateListener():
    def onUpdate(self):
        raise NotImplementedError
class TickListener():
    def onTick(self, secLeft, countingDown):
        raise NotImplementedError
class StartListener():
    def onStart(self, secLeft):
        raise NotImplementedError
class ITimer():
    def setStart(self, withValue = 0):
        raise NotImplementedError
    def pause(self):
        raise NotImplementedError
    def resume(self):
        raise NotImplementedError
    def setSeconds(self, value):
        raise NotImplementedError
    def addSeconds(self, value):
        raise NotImplementedError
    def appendTickListener(self, listener):
        raise NotImplementedError
    def appendStartListener(self, listener):
        raise NotImplementedError
    def onTick(self):
        raise NotImplementedError
class UnthreadedTimer(ITimer, UpdateListener):
    def __init__(self):
        self.tickListeners = []
        self.setStartListeners = []
        self.secondsRemaining = 0
        self.countingDown = False
        self.lastResume = 0
    def onUpdate(self):
        if(self.countingDown):
            if(time.time()-self.lastResume>=1):
                self.secondsRemaining = ( self.secondsRemaining - int(time.time()-self.lastResume) )
                self.onTick()
    def setStart(self, withValue = 0):
        self.secondsRemaining = withValue
        self.resume()
        for listener in self.setStartListeners:
            listener.onStart(self.secondsRemaining)
    def pause(self):
        self.countingDown = False
    def resume(self):
        self.lastResume = time.time()
        self.countingDown = True
    def setSeconds(self, value):
        self.secondsRemaining = value
    def addSeconds(self, value):
        self.secondsRemaining = self.secondsRemaining + value
    def appendTickListener(self, listener):
        self.tickListeners.append(listener)
    def appendStartListener(self, listener):
        self.setStartListeners.append(listener)
    def onTick(self):
        for listener in self.tickListeners:
            listener.onTick(self.secondsRemaining, self.countingDown)
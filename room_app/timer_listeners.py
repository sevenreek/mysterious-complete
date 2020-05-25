class TickObserver():
    def on_tick(self, secLeft, isCountingDown):
        raise NotImplementedError

class TickBasedDisplayUpdater(TickListener):
    def __init__(self, disp : IDisplayController):
        self.disp = disp
    def on_tick(self, seconds, isCountingDown):
        self.disp.setSeconds(seconds)

class TickBasedStatusBroadcaster(TickListener):
    def __init__(self, server : TimerServer):
        self.server = server
    def on_tick(self, seconds, isCountingDown):
        self.server.sendStatusToHost()

class TickBasedHitZeroObserver(TickListener):
    def __init__(self, roomctrl, timer):
        self.timer = timer
    def on_tick(self, seconds, isCountingDown):
        if(seconds == 0 and isCountingDown):   
            self.roomctrl.raiseEvent(GameEvent(BaseGameEvents.TIMER_HITZERO, None)) # this event stops the timer as well
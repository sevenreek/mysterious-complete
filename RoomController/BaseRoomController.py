import datetime
from enum import Enum
from GameEvents import GameEvent, BaseGameEvents
from queue import Queue
# All events(RoomEvent) are passed to the roomcontroller which handles them calling appropriate public functions in gpio, display and timer.
# The room controller holds the current GameState
class GameTimeState():
    STATE_READY     = 0
    STATE_RUNNING   = 1
    STATE_PAUSED    = 2
    STATE_STOPPED   = 3
    def __init__(self, state : int, timeLeft : int, timeStarted = None):
        self.state = state
        self.seconds = timeLeft
        self.startedon = timeStarted
class BaseRoomController():
    def __init__(self, server = None, timer = None, gpio = None):
        self.server = server
        self.timer = timer
        self.gpio = gpio
        self.gameTime = GameTimeState(GameState.STATE_READY, self.timer.secondsRemaining, None) 
        self.eventHandlers = {}
        self.setEventHandlers()
    def setEventHandlers(self):
        self.eventHandlers = {
            BaseGameEvents.EVT_SERVER_PLAY    : self._onGMPlay,
            BaseGameEvents.EVT_SERVER_PAUSE   : self._onGMPause,
            BaseGameEvents.EVT_SERVER_SETTIME : self._onGMSetTime,
            BaseGameEvents.EVT_SERVER_ADDTIME : self._onGMAddTime,
            BaseGameEvents.EVT_SERVER_STOP    : self._onGMStop,
            BaseGameEvents.EVT_SERVER_RESET   : self._onGMReset,
            BaseGameEvents.EVT_TIMER_HITZERO  : self._onTimerHitZero,
            BaseGameEvents.EVT_GPIO_FINISHED  : self._onGPIOLastPuzzle,
            BaseGameEvents.EVT_GPIO_PLAY      : self._onGPIOPlay,
            BaseGameEvents.EVT_GPIO_PAUSE     : self._onGPIOPause,
            BaseGameEvents.EVT_GPIO_STOPRESET : self._onGPIOStop,
            BaseGameEvents.EVT_GPIO_ADDTIME   : self._onGPIOAddTime
        }
    @property
    def roomThemeID(self):
        raise NotImplementedError
    def getTimeState(self):
        return self.gameTime
    def getState(self):
        raise NotImplementedError
    def initialize(self, server = None, timer = None, gpio = None): # due to the circular dependency this function must be called after creating all other controllers
        if(server is not None):
            self.server = server
        if(timer is not None):
            self.timer = timer
        if(gpio is not None):
            self.gpio = gpio
    def raiseEvent(self, roomEvent):
        self.eventHandlers[roomEvent.value](roomEvent)      
    def startGame(self): # the room state can be stopped or ready which means the a game in the room is not in progress and the room is not "active"
        self.timeStarted = "{:02d}:{:02d}".format(datetime.datetime.now().hour, datetime.datetime.now().minute)
        # could probably use datetime.datetime.now().strftime("%R") but this thing works too
    def stopGame(self):
        self.timeStarted = None
    def _onGMPlay(self, roomEvent):
        if(self.roomState.state == STATE_READY): # start game
            self.roomState.state = STATE_RUNNING
            self.gpio.triggerStart()
            self.timer.resume()
            self.setActive()
        elif(self.roomState.state == STATE_PAUSED): # resume game
            self.timer.resume()
            self.roomState.state = STATE_RUNNING
    def _onGMPause(self, roomEvent):
        if(self.roomState.state == STATE_RUNNING): # pause game
            self.roomState.state = STATE_PAUSED
            self.timer.pause()
    def _onGMSetTime(self, roomEvent): # set time to
        self.timer.setSeconds(roomEvent.data)
    def _onGMAddTime(self, roomEvent):
        self.timer.addSeconds(roomEvent.data)
    def _onGMStop(self, roomEvent):
        if(self.roomState.state == STATE_RUNNING or self.roomState.state == STATE_PAUSED):
            self.roomState.state = STATE_STOPPED
            self.timer.pause()
            self.gpio.unlockEntrance()
            self.setUnactive()
    def _onGMReset(self, roomEvent):
        if(self.roomState.state == STATE_STOPPED):
            self.roomState.state = STATE_READY
            self.timer.setSeconds(roomEvent.data)
    # BEGIN TIMER EVENTS
    def _onTimerHitZero(self, roomEvent):
        self.roomState.state = STATE_STOPPED
        self.timer.pause()
        self.gpio.unlockEntrance()
        self.setUnactive()
    # BEGIN GPIO EVENTS
    def _onGPIOLastPuzzle(self, roomEvent): # when finished signal is received, i.e. last puzzle solved
        self.roomState.state = STATE_STOPPED
        self.timer.pause()
        self.gpio.unlockExit()
        self.setUnactive()
    def _onGPIOPlay(self, roomEvent):     
        if(self.roomState.state == STATE_READY): # start game
            self.roomState.state = STATE_RUNNING
            self.timer.setSeconds(CFG_DEFAULT_TIME)
            self.gpio.triggerStart()
            self.timer.resume() 
        elif(self.roomState.state == STATE_PAUSED): # resume game
            self.timer.resume()
            self.roomState.state = STATE_RUNNING
    def _onGPIOPause(self, roomEvent):
        if(self.roomState == STATE_RUNNING): # pause game
            self.timer.pause()
            self.roomState.state = STATE_PAUSED
    def _onGPIOStop(self, roomEvent):
        self.roomState.state = STATE_READY
        self.timer.setSeconds(roomEvent.data)
        self.timer.pause()
        self.gpio.unlockEntrance()
        self.setUnactive()
    def _onGPIOAddTime(self, roomEvent):    
        self.timer.addSeconds(roomEvent.data)

    
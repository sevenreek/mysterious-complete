import datetime
from enum import Enum
from GameEvents import GameEvent, BaseGameEvents
from TimerController import TickListener

# All events(RoomEvent) are passed to the roomcontroller which handles them calling appropriate public functions in gpio, display and timer.
# The room controller holds the current GameState
class GAME_TIME_STATE(Enum):
    READY     = 0
    RUNNING   = 1
    PAUSED    = 2
    STOPPED   = 3
class BaseGameState():
    def __init__(self, state : int = GAME_TIME_STATE.READY, timeLeft : int = 0, timeStarted = None):
        self.state = state
        self.timeleft = timeLeft
        self.startedon = timeStarted
class BaseRoomController():
    def __init__(self, config, server = None, timer = None, gpio = None):
        self.server = server
        self.timer = timer
        self.gpio = gpio
        self.config = config
        self.roomStateContext = None
        self.startedon = None
        self.eventHandlers = {}
    def initialize(self, server = None, timer = None, gpio = None): # due to the circular dependency this function must be called after creating all other controllers
        if(server is not None):
            self.server = server
        if(timer is not None):
            self.timer = timer
        if(gpio is not None):
            self.gpio = gpio
        self.setEventHandlers()
        self.createRoomStateContext()
    def setEventHandlers(self):
        self.eventHandlers = {
            BaseGameEvents.SERVER_PLAY    : self._onGMPlay,
            BaseGameEvents.SERVER_PAUSE   : self._onGMPause,
            BaseGameEvents.SERVER_SETTIME : self._onGMSetTime,
            BaseGameEvents.SERVER_ADDTIME : self._onGMAddTime,
            BaseGameEvents.SERVER_STOP    : self._onGMStop,
            BaseGameEvents.SERVER_RESET   : self._onGMReset,
            BaseGameEvents.TIMER_HITZERO  : self._onTimerHitZero,
            BaseGameEvents.GPIO_FINISHED  : self._onGPIOLastPuzzle,
            BaseGameEvents.GPIO_PLAY      : self._onGPIOPlay,
            BaseGameEvents.GPIO_PAUSE     : self._onGPIOPause,
            BaseGameEvents.GPIO_STOPRESET : self._onGPIOStop,
            BaseGameEvents.GPIO_ADDTIME   : self._onGPIOAddTime
        }
    def createRoomStateContext(self):
        self.roomStateContext = BaseGameState()
    def update(self):
        self.timer.update()
    @property
    def roomThemeID(self):
        raise NotImplementedError
    def getTimeState(self):
        return GameTimeState(state=self.state, timeLeft=self.timer.secondsRemaining, timeStarted=self.startedon)
    def getState(self):
        raise NotImplementedError('Room controller must implement getState()')

    def raiseEvent(self, roomEvent):
        self.eventHandlers[roomEvent.value](roomEvent)      
    def startGame(self): # the room state can be stopped or ready which means the a game in the room is not in progress and the room is not "active"
        self.startedon = "{:02d}:{:02d}".format(datetime.datetime.now().hour, datetime.datetime.now().minute)
        # could probably use datetime.datetime.now().strftime("%R") but this thing works too
    def stopGame(self):
        self.startedon = None
    def _onGMPlay(self, roomEvent):
        if(self.state == GameTimeState.STATE_READY): # start game
            self.state = GameTimeState.STATE_RUNNING
            self.gpio.startRoom()
            self.timer.resume()
        elif(self.state == GameTimeState.STATE_PAUSED): # resume game
            self.timer.resume()
            self.state = GameTimeState.STATE_RUNNING
    def _onGMPause(self, roomEvent):
        if(self.state == GameTimeState.STATE_RUNNING): # pause game
            self.state = GameTimeState.STATE_PAUSED
            self.timer.pause()
    def _onGMSetTime(self, roomEvent): # set time to
        self.timer.setSeconds(roomEvent.data)
    def _onGMAddTime(self, roomEvent):
        self.timer.addSeconds(roomEvent.data)
    def _onGMStop(self, roomEvent):
        if(self.state == GameTimeState.STATE_RUNNING or self.state == GameTimeState.STATE_PAUSED):
            self.state = GameTimeState.STATE_STOPPED
            self.timer.pause()
            self.gpio.unlockEntrance()
    def _onGMReset(self, roomEvent):
        if(self.state == GameTimeState.STATE_STOPPED):
            self.state = GameTimeState.STATE_READY
            self.timer.setSeconds(roomEvent.data)
    # BEGIN TIMER EVENTS
    def _onTimerHitZero(self, roomEvent):
        self.state = GameTimeState.STATE_STOPPED
        self.timer.pause()
        self.gpio.unlockEntrance()
    # BEGIN GPIO EVENTS
    def _onGPIOLastPuzzle(self, roomEvent): # when finished signal is received, i.e. last puzzle solved
        self.state = GameTimeState.STATE_STOPPED
        self.timer.pause()
        self.gpio.unlockExit()
    def _onGPIOPlay(self, roomEvent):     
        if(self.state == GameTimeState.STATE_READY): # start game
            self.state = GameTimeState.STATE_RUNNING
            self.gpio.startRoom()
            self.timer.resume() 
        elif(self.state == GameTimeState.STATE_PAUSED): # resume game
            self.timer.resume()
            self.state = GameTimeState.STATE_RUNNING
    def _onGPIOPause(self, roomEvent):
        if(self == GameTimeState.STATE_RUNNING): # pause game
            self.timer.pause()
            self.state = GameTimeState.STATE_PAUSED
    def _onGPIOStop(self, roomEvent):
        self.state = GameTimeState.STATE_READY
        self.timer.setSeconds(roomEvent.data)
        self.timer.pause()
        self.gpio.unlockEntrance()
    def _onGPIOAddTime(self, roomEvent):    
        self.timer.addSeconds(roomEvent.data)

    

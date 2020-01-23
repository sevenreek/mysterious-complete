from CONFIGURATION import CFG_DEFAULT_TIME
from logger import Logger
import datetime
STATE_READY     = 0
STATE_RUNNING   = 1
STATE_PAUSED    = 2
STATE_STOPPED   = 3

# All events(RoomEvent) are passed to the roomcontroller which handles them calling appropriate public functions in gpio, display and timer.
# The room controller holds the current GameState
class RoomEventListener():
    def raiseEvent(self, event):
        pass
class RoomEvent():    
    EVT_SERVER_PLAY     = 0xA000
    EVT_SERVER_PAUSE    = 0xA001
    EVT_SERVER_SETTIME  = 0xA002
    EVT_SERVER_ADDTIME  = 0xA003
    EVT_SERVER_STOP     = 0xA004
    EVT_SERVER_RESET    = 0xA005
    EVT_TIMER_HITZERO   = 0xB000
    EVT_GPIO_FINISHED   = 0xC000
    EVT_GPIO_PLAY       = 0xC001
    EVT_GPIO_PAUSE      = 0xC002
    EVT_GPIO_STOPRESET  = 0xC003
    EVT_GPIO_ADDTIME    = 0xC004
    namedict = {
        0xA000 : 'EVT_SERVER_PLAY'     ,
        0xA001 : 'EVT_SERVER_PAUSE'    ,
        0xA002 : 'EVT_SERVER_SETTIME'  ,
        0xA003 : 'EVT_SERVER_ADDTIME'  ,
        0xA004 : 'EVT_SERVER_STOP'     ,
        0xA005 : 'EVT_SERVER_RESET'    ,
        0xB000 : 'EVT_TIMER_HITZERO'   ,
        0xC000 : 'EVT_GPIO_FINISHED'   ,
        0xC001 : 'EVT_GPIO_PLAY'       ,
        0xC002 : 'EVT_GPIO_PAUSE'      ,
        0xC003 : 'EVT_GPIO_STOPRESET'  ,
        0xC004 : 'EVT_GPIO_ADDTIME'    
    }
    def __init__(self, value, data=None):
        self.value = value
        self.data = data
class GameState():
    def __init__(self, state, active, timeLeft, timeStarted = None):
        self.state = state
        self.active = active
        self.seconds = timeLeft
        self.startedon = timeStarted
        enddate = datetime.datetime.now() + datetime.timedelta(0,timeLeft)
        self.expecetedend = "{:02d}:{:02d}".format(enddate.hour,enddate.minute)
class MainRoomController(RoomEventListener): 
    def __init__(self, server = None, timer = None, gpio = None):
        self.server = server
        self.timer = timer
        self.gpio = gpio
        self.roomState = STATE_READY
        self.gameActive = False
        self.timeStarted = None
    def initialize(self, server = None, timer = None, gpio = None): # due to the circular dependency this function must be called after creating all other controllers
        if(server is not None):
            self.server = server
        if(timer is not None):
            self.timer = timer
        if(gpio is not None):
            self.gpio = gpio
    def _onEvent(self, roomEvent):
        try:
            Logger.glog("Received event: {0}; data: {1}".format(RoomEvent.namedict[roomEvent.value], str(roomEvent.data)))
        except Exception as e:
            print("Logging failed")
            print(str(e))
        # BEGIN SERVER EVENTS
        if(roomEvent.value == RoomEvent.EVT_SERVER_PLAY):
            if(self.roomState == STATE_READY): # start game
                self.roomState = STATE_RUNNING
                self.gpio.triggerStart()
                self.timer.resume()
                self.setActive()
            elif(self.roomState == STATE_PAUSED): # resume game
                self.timer.resume()
                self.roomState = STATE_RUNNING
        elif(roomEvent.value == RoomEvent.EVT_SERVER_PAUSE):
            if(self.roomState == STATE_RUNNING): # pause game
                self.roomState = STATE_PAUSED
                self.timer.pause()
        elif(roomEvent.value == RoomEvent.EVT_SERVER_SETTIME): # set time to
            self.timer.setSeconds(roomEvent.data)
        elif(roomEvent.value == RoomEvent.EVT_SERVER_ADDTIME): # add time
            self.timer.addSeconds(roomEvent.data)
        elif(roomEvent.value == RoomEvent.EVT_SERVER_STOP): # stop game
            if(self.roomState == STATE_RUNNING or self.roomState == STATE_PAUSED):
                self.roomState = STATE_STOPPED
                self.timer.pause()
                self.gpio.unlockEntrance()
                self.setUnactive()
        elif(roomEvent.value == RoomEvent.EVT_SERVER_RESET): # reset game from stopped
            if(self.roomState == STATE_STOPPED):
                self.roomState = STATE_READY
                self.timer.setSeconds(roomEvent.data)
        # BEGIN TIMER EVENTS
        elif(roomEvent.value == RoomEvent.EVT_TIMER_HITZERO): # when timer runs out
            self.roomState = STATE_STOPPED
            self.timer.pause()
            self.gpio.unlockEntrance()
            self.setUnactive()
        # BEGIN GPIO EVENTS
        elif(roomEvent.value == RoomEvent.EVT_GPIO_FINISHED): # when finished signal is received, i.e. last puzzle solved
            self.roomState = STATE_STOPPED
            self.timer.pause()
            self.gpio.unlockExit()
            self.setUnactive()
        elif(roomEvent.value == RoomEvent.EVT_GPIO_PLAY):     
            if(self.roomState == STATE_READY): # start game
                self.roomState = STATE_RUNNING
                self.timer.setSeconds(CFG_DEFAULT_TIME)
                self.gpio.triggerStart()
                self.timer.resume() 
            elif(self.roomState == STATE_PAUSED): # resume game
                self.timer.resume()
                self.roomState = STATE_RUNNING
        elif(roomEvent.value == RoomEvent.EVT_GPIO_PAUSE):     
            if(self.roomState == STATE_RUNNING): # pause game
                self.timer.pause()
                self.roomState = STATE_PAUSED
        elif(roomEvent.value == RoomEvent.EVT_GPIO_STOPRESET):       
            self.roomState = STATE_READY
            self.timer.setSeconds(roomEvent.data)
            self.timer.pause()
            self.gpio.unlockEntrance()
            self.setUnactive()
        elif(roomEvent.value == RoomEvent.EVT_GPIO_ADDTIME):    
            self.timer.addSeconds(roomEvent.data)
        return GameState(self.roomState, self.gameActive, self.timer.secondsRemaining, self.timeStarted)
    def raiseEvent(self, roomEvent):
        return self._onEvent(roomEvent)
    def getState(self):
        return GameState(self.roomState, self.gameActive, self.timer.secondsRemaining, self.timeStarted)
    def setActive(self): # the room state can be stopped or ready which means the a game in the room is not in progress and the room is not "active"
        self.gameActive = True
        self.timeStarted = "{:02d}:{:02d}".format(datetime.datetime.now().hour, datetime.datetime.now().minute)
    def setUnactive(self):
        self.gameActive = False
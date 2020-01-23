from roomController import MainRoomController, RoomEvent
import RPi.GPIO as GPIO
from CONFIGURATION import CFG_DEFAULT_TIME
from logger import Logger
CFG_PIN_PLAY = 14
CFG_PIN_PAUSE = 15
CFG_PIN_STOP_AND_RESET = 18
CFG_PIN_ADD_TIME = 23
CFG_ADD_TIME_VALUE = 300 # in seconds
CFG_PIN_START_ROOM = 17
CFG_PIN_ENTRANCE_OPEN = 27
CFG_PIN_EXIT_OPEN = 22
CFG_START_VALUE = 1
CFG_EXIT_OPEN_VALUE = 1
CFG_ENTRANCE_OPEN_VALUE = 1
CFG_PIN_LAST_PUZZLE = 24
CFG_DEBOUNCE_TIME = 200
class GPIOController():
    def __init__(self, roomctrl):
        self.roomctrl = roomctrl
        GPIO.setmode(GPIO.BCM)
        GPIO.setup( CFG_PIN_PLAY,            GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup( CFG_PIN_PAUSE,           GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup( CFG_PIN_STOP_AND_RESET,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup( CFG_PIN_ADD_TIME,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup( CFG_PIN_LAST_PUZZLE,     GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup( CFG_PIN_START_ROOM,      GPIO.OUT)
        GPIO.setup( CFG_PIN_ENTRANCE_OPEN,   GPIO.OUT)
        GPIO.setup( CFG_PIN_EXIT_OPEN,       GPIO.OUT)
        GPIO.output( CFG_PIN_START_ROOM,     not CFG_START_VALUE)
        GPIO.output( CFG_PIN_EXIT_OPEN,      not CFG_EXIT_OPEN_VALUE)
        GPIO.output( CFG_PIN_ENTRANCE_OPEN,  not CFG_ENTRANCE_OPEN_VALUE)
        GPIO.add_event_detect( CFG_PIN_PLAY,             GPIO.FALLING, callback=self.onPlayBtn,      bouncetime=CFG_DEBOUNCE_TIME)
        GPIO.add_event_detect( CFG_PIN_PAUSE,            GPIO.FALLING, callback=self.onPauseBtn,     bouncetime=CFG_DEBOUNCE_TIME)
        GPIO.add_event_detect( CFG_PIN_STOP_AND_RESET,   GPIO.FALLING, callback=self.onResetBtn,     bouncetime=CFG_DEBOUNCE_TIME)
        GPIO.add_event_detect( CFG_PIN_ADD_TIME,         GPIO.FALLING, callback=self.onAddTimeBtn,   bouncetime=CFG_DEBOUNCE_TIME)
        GPIO.add_event_detect( CFG_PIN_LAST_PUZZLE,      GPIO.FALLING, callback=self.onLastPuzzle,   bouncetime=CFG_DEBOUNCE_TIME)
        Logger.glog("Loaded GPIO controller.")
    def unlockEntrance(self):
        GPIO.output(CFG_PIN_ENTRANCE_OPEN, CFG_ENTRANCE_OPEN_VALUE)
        Logger.glog("Unlocking entrance.")
    def unlockExit(self):
        GPIO.output(CFG_PIN_EXIT_OPEN, CFG_EXIT_OPEN_VALUE)
        Logger.glog("Unlocking exit.")
    def triggerStart(self):
        GPIO.output(CFG_PIN_START_ROOM, CFG_START_VALUE)
        Logger.glog("Triggering game start.")
    def lockEntrance(self):
        GPIO.output(CFG_PIN_ENTRANCE_OPEN, not CFG_ENTRANCE_OPEN_VALUE)
        Logger.glog("Locking entrance.")
    def lockExit(self):
        GPIO.output(CFG_PIN_EXIT_OPEN, not CFG_EXIT_OPEN_VALUE)
        Logger.glog("Locking exit.")
    def onAddTimeBtn(self, channel):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_ADDTIME, CFG_ADD_TIME_VALUE))
        Logger.glog("GPIO time add triggered.")
    def onPlayBtn(self, channel):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_PLAY))
        Logger.glog("GPIO play triggered.")
    def onResetBtn(self, channel):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_STOPRESET, CFG_DEFAULT_TIME))
        Logger.glog("GPIO reset triggered.")
    def onPauseBtn(self, channel):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_PAUSE))
        Logger.glog("GPIO pause triggered.")
    def onLastPuzzle(self, channel):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_FINISHED))
        Logger.glog("GPIO last puzzle triggered.")
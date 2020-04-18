
from BaseRoomController import BaseRoomController
import RPi.GPIO as GPIO
from Config import BaseGPIOConfig
from logger import Logger
from time import sleep


class GPIODevice():
    def getStateDict(self) -> dict:
        raise NotImplementedError
class TestStatusDevice(GPIODevice):
    def getStateDict(self):
        return {'test' : success}
class PulseDoorLock(GPIODevice):
    def __init__(self, pin_entrance : int, pin_exit : int, open_voltage : int = 1, pulseduration : float = 0.01):
        self.exitOpen = False
        self.entranceOpen = False
        self.pinEntrance = pin_entrance
        self.pinExit = pin_exit
        self.open_voltage = open_voltage
        self.pulseDuration = pulseduration
        GPIO.setup(self.pinEntrance, GPIO.OUT)
        GPIO.setup(self.pinExit, GPIO.OUT)
        GPIO.output(self.pinEntrance, not self.open_voltage)
        GPIO.output(self.pinExit, not self.open_voltage)
    def openEntrance(self):
        self.entranceOpen = True
        GPIO.output(self.pinEntrance, self.open_voltage)
        sleep(self.pulseDuration)
        GPIO.output(self.pinEntrance, not self.open_voltage)
    def openExit(self):
        self.exitOpen = True
        GPIO.output(self.pinExit, self.open_voltage)
        sleep(self.pulseDuration)
        GPIO.output(self.pinExit, not self.open_voltage)
    def resetExit(self):
        self.exitOpen = False
        GPIO.output(self.pinExit, not self.open_voltage)
    def resetEntrance(self):
        self.entranceOpen = False
        GPIO.output(self.pinEntrance, not self.open_voltage)
    def getStateDict(self):
        return {'exit_open' : self.exitOpen, 'entrance_open' : self.entranceOpen}
class BaseControlPanel(GPIODevice):
    def getStateDict(self):
        return None
    def __init__(self, eventSystem : BaseRoomController.BaseRoomController, btn_play : int, btn_reset : int, btn_addtime : int, btn_pause : int, pullupdown, debounce : int = 100):
        self.buttonPlay = btn_play
        self.buttonReset = btn_reset
        self.buttonAdd = btn_addtime
        self.buttonPause = btn_pause
        self.eventSystem = eventSystem
        GPIO.setup(self.buttonPlay,  GPIO.IN, pull_up_down=pullupdown)
        GPIO.setup(self.buttonReset, GPIO.IN, pull_up_down=pullupdown)
        GPIO.setup(self.buttonAdd,   GPIO.IN, pull_up_down=pullupdown)
        GPIO.setup(self.buttonPause, GPIO.IN, pull_up_down=pullupdown)
        edgedetect = GPIO.FALLING if pullupdown==GPIO.PUD_UP else GPIO.RISING
        GPIO.add_event_detect( self.buttonPlay,  edgedetect, callback=self.onPlayBtn,    bouncetime=debounce)
        GPIO.add_event_detect( self.buttonReset, edgedetect, callback=self.onResetBtn,   bouncetime=debounce)
        GPIO.add_event_detect( self.buttonAdd,   edgedetect, callback=self.onAddTimeBtn, bouncetime=debounce)
        GPIO.add_event_detect( self.buttonPause, edgedetect, callback=self.onPauseBtn,   bouncetime=debounce)
    def onAddTimeBtn(self, channel):
        self.eventSystem.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_ADDTIME, CFG_ADD_TIME_VALUE))
    def onPlayBtn(self, channel):
        self.eventSystem.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_PLAY))
    def onResetBtn(self, channel):
        self.eventSystem.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_STOPRESET, CFG_DEFAULT_TIME))
    def onPauseBtn(self, channel):
        self.eventSystem.raiseEvent(RoomEvent(RoomEvent.EVT_GPIO_PAUSE))
class StartTrigger(GPIODevice): 
    def __init__(self, pin_hold : int, pin_pulse : int, on_voltage : int = 1, pulseduration : float = 0.01):
        self.pinPulse = False # upon start one pin is pulsed with on_voltage one is held until reset
        self.pinHold = False
        self.onVoltage = on_voltage
        self.pulseDuration = pulseduration
        GPIO.setup(self.pinPulse, GPIO.OUT)
        GPIO.setup(self.pinHold,  GPIO.OUT)
        GPIO.output(self.pinPulse, not self.onVoltage)
        GPIO.output(self.pinHold, not self.onVoltage)
    def start(self):
        GPIO.output(self.pinHold, self.onVoltage)
        GPIO.output(self.pinPulse, self.onVoltage)
        sleep(self.pulseDuration)
        GPIO.output(self.pinPulse, not self.onVoltage)
    def reset(self):
        GPIO.output(self.pinHold, not self.onVoltage)
    def getStateDict(self):
        return None # returns none since it is tied directly to timer states, so information is redundant

class BaseGPIOController():
    def __init__(self, roomctrl : BaseRoomController.BaseRoomController, config : BaseGPIOConfig):
        GPIO.setmode(GPIO.BCM)
        self.roomctrl = roomctrl
        self.controlPanel = BaseControlPanel(roomctrl, config.BTN_PLAY, config.BTN_STOP_AND_RESET, config.BTN_ADD_TIME, config.BTN_PAUSE, config.PULLUP_MODE, config.DEBOUNCE_TIME)
        self.doorLock = PulseDoorLock(config.PIN_ENTRANCE_OPEN, config.PIN_EXIT_OPEN, config.DOOR_OPEN_VOLTAGE, config.TRIGGER_HOLD_TIME)
        self.testPeripheral = TestStatusDevice()
        self.gpioDevices = []
        self.fillGPIODevices()
    def fillGPIODevices(self):
        self.gpioDevices = [self.testPeripheral, self.doorLock]
    def getPeripheralStatus(self) -> dict:
        dct = {}
        for d in self.gpioDevices:
            peripheralStatus = d.getStateDict()
            if(peripheralStatus is not None):
                dct.update(peripheralStatus)
        return dct

        
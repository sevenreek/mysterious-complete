from RoomControllers import RoomIDs
import RPi
class RoomConfig():
    # Feel free to edit these
    ROOM_NAME = "Test Room #1"
    DEFAULT_TIME = 3600 # in seconds
    ROOM_UNIQUE_ID = 0xDE00 | RoomIDs.DEBUGROOM.value # device ID has to have the format of 0xDE%%
    ALLOW_SUDO = True # allows execution of arbitrary sudo command from http request; 
                      # extreme security risk if anyone from outside connects to the network;
                      # keep False if not debugging
    STATUS_BROADCAST_REPEAT_PERIOD_UNLINKED = 5 # sec
    STATUS_BROADCAST_REPEAT_PERIOD_LINKED = 1
    # Probably don't touch these
    I2C_FREQUENCY = 100000
    LOGS_DIR = 'logs' 
    LOGS_DATE_FORMAT = '%Y-%m-%d'
    LOGS_TIME_FORMAT = '[%H:%M:%S] '
    LOGS_DAYS_ARCHIVE_SIZE = 7
    UDP_DETECT_BROADCAST_PORT = 4000
    HTTP_SERVER_PORT = 8080
    HTTP_SEVER_HOST = '0.0.0.0'
class BaseGPIOConfig():
    TRIGGER_HOLD_TIME = 0.025 # seconds
    BTN_PLAY = 14
    BTN_PAUSE = 15
    BTN_STOP_AND_RESET = 18
    BTN_ADD_TIME = 23
    ADD_TIME_VALUE = 300 # in seconds
    PIN_START_ROOM_TRIGGER = 25 # this only gets held at CFG_START_VALUE for CFG_TRIGGER_HOLD_TIME upon triggerStart()
    PIN_START_ROOM_HOLD = 17 # this one remains at CFG_START_VALUE after triggerStart()
    PIN_ENTRANCE_OPEN = 27
    PIN_EXIT_OPEN = 22
    START_VOLTAGE = 1
    DOOR_OPEN_VOLTAGE = 1
    PIN_LAST_PUZZLE = 24
    DEBOUNCE_TIME = 200
    PULLUP_MODE = RPi.GPIO.PUD_UP

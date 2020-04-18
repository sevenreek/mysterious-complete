from enum import Enum
class BaseGameEvents(Enum):
    SERVER_PLAY     = 0x0000
    SERVER_PAUSE    = 0x0001
    SERVER_SETTIME  = 0x0002
    SERVER_ADDTIME  = 0x0003
    SERVER_STOP     = 0x0004
    SERVER_RESET    = 0x0005
    TIMER_HITZERO   = 0x0100
    GPIO_FINISHED   = 0x0200
    GPIO_PLAY       = 0x0201
    GPIO_PAUSE      = 0x0202
    GPIO_STOPRESET  = 0x0203
    GPIO_ADDTIME    = 0x0204
class DebugGameEvents(Enum):
    TEST0_SUBTEST0 = 0xF000
    TEST0_SUBTEST1 = 0xF001
    TEST1_SUBTEST0 = 0xF100
class GameEvent():    
    def __init__(self, value, data=None):
        self.value = value
        self.data = data
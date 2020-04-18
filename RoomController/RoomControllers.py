from enum import Enum
from BaseRoomController import BaseRoomController


class RoomIDs(Enum):
    DEBUGROOM = 0

class DebugRoomController(BaseRoomController): 
    def __init__(self, server = None, timer = None, gpio = None):
        super().__init__(server, timer, gpio)
        self.roomThemeID = RoomIDs.MAIN_IMPL
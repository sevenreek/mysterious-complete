from enum import Enum
from BaseRoomController import BaseRoomController


class RoomIDs(Enum):
    DEBUGROOM = 0

class DebugRoomController(BaseRoomController): 
    def __init__(self, server = None, timer = None, gpio = None):
        super().__init__(server, timer, gpio)
    @property
    def roomThemeID(self):
        return RoomIDs.DEBUGROOM
    def getState(self):
        sdict = {
            'id' : self.config.ROOM_UNIQUE_ID,
            'name' : self.config.ROOM_NAME,
            'gm' : self.server._gameMasterIP
        }
        sdict.update(vars(self.gameTimeState))
        return sdict

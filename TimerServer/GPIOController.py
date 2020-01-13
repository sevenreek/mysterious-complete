from roomController import MainRoomController
class GPIOController():
    def __init__(self, roomctrl):
        self.roomctrl = roomctrl
    def configurePin(self, pin, pinmode):
        pass
    def setPin(self, pin):
        pass
    def clearPin(self, pin):
        pass
    def configureInput(self, pin, func):
        pass
    def unlockEntrance(self):
        pass
    def unlockExit(self):
        pass
    def triggerStart(self):
        pass
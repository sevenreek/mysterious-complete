import busio
import board
from TimerController import UnthreadedTimer
from GPIOController import BaseGPIOController
from DisplayController import AF_HT16K33_7Seg, CommandLineDisplay
from Server import TimerServer
from Config import RoomConfig, BaseGPIOConfig, ServerConfig
from RoomControllers import DebugRoomController
def main():
    cfg = RoomConfig()
    gpiocfg = BaseGPIOConfig()
    servercfg = ServerConfig()
    roomname = cfg.ROOM_NAME
    roomController = DebugRoomController(cfg)
    gpio = BaseGPIOController(roomController, gpiocfg)
    dsp = None
    try:
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        dsp = AF_HT16K33_7Seg(i2c)
    except:
        print("FAILED TO LOAD I2C DISPLAY! LOADING DEBUG CONSOLE DISPLAY!")
        dsp = CommandLineDisplay()
    tmr = UnthreadedTimer(roomController)
    tmr.appendTickListener(dsp)
    tmr.setSeconds(cfg.DEFAULT_TIME)
    server = TimerServer(roomController, servercfg)
    roomController.initialize(server,tmr,gpio)
    server.startThreaded()
    while(True):
        tmr.onUpdate()


if __name__ == "__main__":
    main()




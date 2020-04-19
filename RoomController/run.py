import busio
import board
from TimerController import UnthreadedTimer
from DisplayController import AF_HT16K33_7Seg, CommandLineDisplay
from Server import TimerServer
from Config import RoomConfig
from RoomControllers import DebugRoomController
def main():
    cfg = RoomConfig()
    roomname = cfg.ROOM_NAME
    roomController = MainRoomController()
    gpio = GPIOController(roomController)
    dsp = None
    try:
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        dsp = AF_HT16K33_7Seg(i2c)
    except:
        print("FAILED TO LOAD I2C DISPLAY! LOADING DEBUG CONSOLE DISPLAY!")
        dsp = CommandLineDisplay()
    tmr = UnthreadedTimer(roomController)
    tmr.appendTickListener(dsp)
    tmr.setSeconds(CFG_DEFAULT_TIME)
    server = TimerServer(tmr, CFG_ROOM_UNIQUE_ID, roomname, CFG_HTTP_SEVER_HOST, CFG_HTTP_SERVER_PORT, CFG_UDP_DETECT_BROADCAST_PORT, roomController)
    roomController.initialize(server,tmr,gpio)
    server.broadcastSelf()
    server.startThreaded()
    while(True):
        tmr.onUpdate()


if __name__ == "__main__":
    main()




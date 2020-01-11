import busio
import board
from timerController import UnthreadedTimer
from displayController import AF_HT16K33_7Seg, CommandLineDisplay
from timerServer import TimerServer
from CONFIGURATION import *
def test_justTimer():
    tmr = UnthreadedTimer()
    i2c = busio.I2C(board.SCL, board.SDA)
    dsp = AF_HT16K33_7Seg(i2c)
    tmr.appendTickListener(dsp)
    tmr.setStart(3600)
    while(True):
        tmr.onUpdate()

def test_timerHTTP():
    tmr = UnthreadedTimer()
    roomname = CFG_ROOM_NAME
    dsp = None
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        dsp = AF_HT16K33_7Seg(i2c)
    except:
        print("FAILED TO LOAD I2C DISPLAY! LOADING DEBUG CONSOLE DISPLAY!")
        print("FAILED TO LOAD I2C DISPLAY! LOADING DEBUG CONSOLE DISPLAY!")
        print("FAILED TO LOAD I2C DISPLAY! LOADING DEBUG CONSOLE DISPLAY!")
        dsp = CommandLineDisplay()
        roomname += "[ERROR]"
    tmr.appendTickListener(dsp)
    tmr.appendEventListener(dsp)
    tmr.setStart(3600)
    server = TimerServer(tmr, roomname, CFG_HTTP_SEVER_HOST, CFG_HTTP_SERVER_PORT, CFG_UDP_DETECT_BROADCAST_PORT)
    tmr.appendEventListener(server)
    tmr.pause()
    server.broadcastSelf()
    server.startThreaded()
    while(True):
        tmr.onUpdate()


if __name__ == "__main__":
    test_timerHTTP()




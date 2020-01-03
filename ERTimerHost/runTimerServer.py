import busio
import board
from timerController import UnthreadedTimer
from displayController import AF_HT16K33_7Seg
from timerServer import TimerServer
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
    i2c = busio.I2C(board.SCL, board.SDA)
    dsp = AF_HT16K33_7Seg(i2c)
    tmr.appendTickListener(dsp)
    tmr.setStart(3600)
    server = TimerServer(tmr,'Test Room #1','0.0.0.0', 8080, 4000)
    tmr.pause()
    server.broadcastSelf()
    server.startThreaded()
    while(True):
        tmr.onUpdate()


if __name__ == "__main__":
    test_timerHTTP()




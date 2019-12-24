import busio
import board
from timerController import UnthreadedTimer
from displayController import AF_HT16K33_7Seg
def test_01():
    tmr = UnthreadedTimer()
    i2c = busio.I2C(board.SCL, board.SDA)
    dsp = AF_HT16K33_7Seg(i2c)
    tmr.appendTickListener(dsp)
    while(True):
        tmr.onUpdate()

if __name__ == "__main__":
    test_01()




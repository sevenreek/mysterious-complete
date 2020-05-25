import busio
import board
from TimerController import UnthreadedTimer
import TimerListeners
from GPIOController import BaseGPIOController
from DisplayController import AF_HT16K33_7Seg, CommandLineDisplay, IDisplayController
import room_app.base_server as base_server
from Room import RoomConfig, BaseGPIOConfig, ServerConfig
from RoomControllers import DebugRoomController
from GameEvents import GameEvent, BaseGameEvents
def main():
    cfg = RoomConfig()
    gpiocfg = BaseGPIOConfig()
    servercfg = ServerConfig()
    roomname = cfg.ROOM_NAME
    roomController = DebugRoomController(cfg)
    gpio = BaseGPIOController(roomController, gpiocfg)
    dsp = None
    try:
        i2c = busio.I2C(board.SCL, board.SDA, frequency=gpiocfg.I2C_FREQUENCY)
        dsp = AF_HT16K33_7Seg(i2c)
    except:
        print("FAILED TO LOAD I2C DISPLAY! LOADING DEBUG CONSOLE DISPLAY!")
        dsp = CommandLineDisplay()
    tmr = UnthreadedTimer()
    tmr.setSeconds(cfg.DEFAULT_TIME)
    server = base_server.BaseServer(roomController, servercfg)
    roomController.initialize(server, tmr, gpio)
    tmr.appendTickListener(TimerListeners.TickBasedStatusBroadcaster(server))
    tmr.appendTickListener(TimerListeners.TickBasedHitZeroObserver(roomController, tmr))
    tmr.appendTickListener(TimerListeners.TickBasedDisplayUpdater(dsp))
    server.startThreaded()
    while(True):
        roomController.update()


if __name__ == "__main__":
    main()




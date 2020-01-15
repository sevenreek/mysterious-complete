from bottle import Bottle, route, run, template, request, response
from roomdevices import ROOMDEVICES
from roomController import RoomEvent
import time
import threading
import socket
import json
class TimerServer():
    BROADCAST_REPEAT_PERIOD = 30
    def __init__(self, timerInterface, roomID, roomName, host, port, broadcastPort, roomController):
        self._timerSocket = timerInterface
        self._host = host
        self._port = port
        self._broadcastPort = broadcastPort
        self._roomID = roomID
        self._roomName = roomName
        self.roomctrl = roomController
        self._linked = False
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: # try to obtain local ip of device
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            self._deviceIP = s.getsockname()[0]
        except:
            self._deviceIP = '127.0.0.1'
        finally:
            s.close()
        self._bottleApp = Bottle()
        self._route()
    def _route(self):
        self._bottleApp.route('/timer/status', method="GET", callback=self._status)
        self._bottleApp.route('/timer/pause', method="GET", callback=self._pause)
        self._bottleApp.route('/timer/play', method="GET", callback=self._play)
        self._bottleApp.route('/timer/stop', method="GET", callback=self._stop)
        self._bottleApp.route('/timer/set', method="GET", callback=self._set)
        self._bottleApp.route('/timer/reset', method="GET", callback=self._reset)
        self._bottleApp.route('/timer/add', method="GET", callback=self._add)
        self._bottleApp.route('/link', method="GET", callback=self._link)
        self._bottleApp.route('/unlink', method="GET", callback=self._unlink)
        self._bottleApp.route('/broadcast', method="GET", callback=self.broadcastSelf)
        self._bottleApp.route('/who', method="GET", callback=self._who)
        self._bottleApp.add_hook('after_request', func=self._enable_cors)
    def _status(self):
        jsonf = json.dumps(self.roomctrl.getState().__dict__) 
        return jsonf
    def _pause(self):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_PAUSE))
        return self._status()
    def _play(self):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_PLAY))
        return self._status()
    def _stop(self):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_STOP))
        return self._status()
    def _set(self):
        try:
            seconds = int(request.query.get('totalseconds'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_SETTIME, seconds))
        except (ValueError, TypeError) as e:
            print(e)
            return self._status() 
        return self._status()
    def _add(self):
        try:
            seconds = int(request.query.get('totalseconds'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_ADDTIME, seconds))
            return self._status()
        except (ValueError, TypeError) as e:
            print(e)
            return self._status()
    def _reset(self):
        try:
            seconds = int(request.query.get('totalseconds'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_RESET, seconds))
            return self._status()
        except (ValueError, TypeError) as e:
            print(e)
            return self._status()
    def startServer(self):
        self._bottleApp.run(host=self._host, port=self._port)
    def broadcastSelf(self):
        broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        jsonFile = json.dumps(
            ( 
            ROOMDEVICES.MODEL_RPI,
            self._roomID,
            self._roomName
            )
        )
        byteSequence = bytes(jsonFile, 'utf-8') 
        broadcastSocket.sendto( byteSequence, ('255.255.255.255', self._broadcastPort) )
        broadcastSocket.close()
        return 'forced broadcast'
    def broadcastContinous(self):
        while(not self._linked):
            self.broadcastSelf()
            time.sleep(self.BROADCAST_REPEAT_PERIOD)
    def _who(self):
        return json.dumps(
            ( 
            ROOMDEVICES.MODEL_RPI,
            self._roomID,
            self._roomName
            )
        )
    def _link(self):
        self._linked = True
        return self._who()
    def _unlink(self):
        self._linked = False
        threading.Thread(target=self.broadcastContinous).start()
    def _enable_cors(self):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    def startThreaded(self):
        threading.Thread(target=self.broadcastContinous).start()
        threading.Thread(target=self.startServer).start()
    
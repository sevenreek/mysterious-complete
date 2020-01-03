from bottle import Bottle, route, run, template, request, response
from roomdevices import ROOMDEVICES
import threading
import socket
import json
class TimerEventListener():
    def onEvent(self, event):
        raise NotImplementedError
class TimerServer():
    STATE_NULL        = 0
    STATE_READY       = 1
    STATE_STARTED     = 2
    STATE_RESUMED     = 3
    STATE_PAUSED      = 4
    STATE_STOPPED_END = 5
    STATE_STOPPED_WIN = 6
    def __init__(self, timerInterface, roomID, host, port, broadcastPort):
        self._timerSocket = timerInterface
        self._host = host
        self._port = port
        self._broadcastPort = broadcastPort
        self._roomID = roomID
        self._state = TimerServer.STATE_READY
        self.eventListeners = []
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
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
        self._bottleApp.route('/broadcast', method="GET", callback=self.broadcastSelf)
        self._bottleApp.route('/who', method="GET", callback=self._who)
        self._bottleApp.add_hook('after_request', func=self._enable_cors)
    def _status(self):
        timerState = self._timerSocket.getStatus()
        totalSeconds = timerState[0]
        timerRunning = timerState[1]
        return json.dumps((totalSeconds, timerRunning, self._state))
    def _pause(self):
        self._timerSocket.pause()
        if(self._state == TimerServer.STATE_STARTED or self._state == TimerServer.STATE_RESUMED):
            self._state = TimerServer.STATE_PAUSED
            self.notifyStateChangeListeners(self._state)
        return self._status()
    def _play(self):
        self._timerSocket.resume()
        if(self._state == TimerServer.STATE_READY):
            self._state = TimerServer.STATE_STARTED
        else:
            self._state = TimerServer.STATE_RESUMED
        self.notifyStateChangeListeners(self._state)
        return self._status()
    def _stop(self):
        self._timerSocket.pause()
        self._state = TimerServer.STATE_STOPPED_END
        self.notifyStateChangeListeners(self._state)
        return self._status()
    def _set(self):
        try:
            seconds = int(request.query.get('totalseconds'))
            self._timerSocket.setSeconds(seconds)
        except (ValueError, TypeError) as e:
            return self._status() 
        return self._status()
    def _add(self):
        try:
            seconds = int(request.query.get('totalseconds'))
            self._timerSocket.addSeconds(seconds)
            return self._status()
        except (ValueError, TypeError) as e:
            return self._status()
    def _reset(self):
        try:
            seconds = int(request.query.get('totalseconds'))
            self._timerSocket.setSeconds(seconds)
            self._timerSocket.pause()
            self._state = TimerServer.STATE_READY
            self.notifyStateChangeListeners(self._state)
            return self._status()
        except (ValueError, TypeError) as e:
            return self._status()
    def startServer(self):
        self._bottleApp.run(host=self._host, port=self._port)
    def broadcastSelf(self):
        broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        jsonFile = json.dumps(
            ( 
            ROOMDEVICES.MODEL_RPI,
            (ROOMDEVICES.TAG_WHO, ROOMDEVICES.TAG_TIMER),
            self._roomID
            )
        )
        byteSequence = bytes(jsonFile, 'utf-8') 
        broadcastSocket.sendto( byteSequence, ('255.255.255.255', self._broadcastPort) )
        broadcastSocket.close()
        return 'forced broadcast'
    def _who(self):
        return json.dumps(
            ( 
            ROOMDEVICES.MODEL_RPI,
            (ROOMDEVICES.TAG_WHO, ROOMDEVICES.TAG_TIMER),
            self._roomID
            )
        ) # this should become a JSON eventually
    def _enable_cors(self):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    def startThreaded(self):
        threading.Thread(target=self.startServer).start()
    def appendListener(self, listener):
        self.eventListeners.append(listener)
    def notifyStateChangeListeners(self, newState):
        for listener in self.eventListeners:
            listener.onEvent(newState)
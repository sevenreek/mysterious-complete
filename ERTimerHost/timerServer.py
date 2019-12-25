from bottle import Bottle, route, run, template, request
from roomdevices import ROOMDEVICES
import threading
import socket
class TimerServer():
    def __init__(self, timerInterface, roomID, host, port, broadcastPort):
        self._timerSocket = timerInterface
        self._host = host
        self._port = port
        self._broadcastPort = broadcastPort
        self._roomID = roomID
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
        self._bottleApp.route('/timer/resume', method="GET", callback=self._resume)
        self._bottleApp.route('/timer/set', method="GET", callback=self._set)
        self._bottleApp.route('/timer/add', method="GET", callback=self._add)
        self._bottleApp.route('/who', method="GET", callback=self._who)
    def _status(self):
        timerState = self._timerSocket.getStatus()
        totalSeconds = timerState[0]
        timerRunning = timerState[1]
        return '{0}<br/>{1}'.format(totalSeconds, timerRunning)
    def _pause(self):
        self._timerSocket.pause()
        return self._status() + '<br/>PAUSED'
    def _resume(self):
        self._timerSocket.resume()
    def _set(self):
        try:
            seconds = int(request.query.get('totalseconds'))
            self._timerSocket.setSeconds(seconds)
        except ValueError:
            return self._status() + '<br/>FAILED VALUE PARSE!'
        return self._status() + '<br/>TIME SET!'
    def _add(self):
        try:
            seconds = int(request.query.get('totalseconds'))
            self._timerSocket.addSeconds(seconds)
            return self._status() + '<br/>TIME ADDED!'
        except ValueError:
            return self._status() + '<br/>FAILED VALUE PARSE!'
    def start(self):
        self._bottleApp.run(host=self._host, port=self._port)
    def broadcastSelf(self):
        broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        byteSequence =  bytes(
            '{0}\n{1}\n{2}'.format(
                ROOMDEVICES.MODEL_RPI,
                (ROOMDEVICES.TAG_WHO, ROOMDEVICES.TAG_TIMER),
                self._roomID
        ), 'utf-8') # this should become a JSON eventually
        broadcastSocket.sendto( byteSequence, ('255.255.255.255', self._broadcastPort) )
        broadcastSocket.close()
    def _who(self):
        return '{0}\n{1}\n{2}'.format( 
            ROOMDEVICES.MODEL_RPI,
            (ROOMDEVICES.TAG_WHO, ROOMDEVICES.TAG_TIMER),
            self._roomID
        ) # this should become a JSON eventually
    def startThreaded(self):
        threading.Thread(target=self.start).start()

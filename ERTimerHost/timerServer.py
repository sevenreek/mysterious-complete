from bottle import Bottle, route, run, template, request
import threading
import socket
class TimerServer():
    def __init__(self, timerInterface, roomID, host, port):
        self._timerSocket = timerInterface
        self._host = host
        self._port = port
        self._roomID = roomID
        self._deviceName = socket.gethostname()
        self._deviceIP = socket.gethostbyname(self._deviceName)[-1]
        self._bottleApp = Bottle()
        self._route()
    def _route(self):
        self._bottleApp.route('/timer/status', method="GET", callback=self._status)
        self._bottleApp.route('/timer/pause', method="GET", callback=self._pause)
        self._bottleApp.route('/timer/resume', method="GET", callback=self._resume)
        self._bottleApp.route('/timer/set', method="GET", callback=self._set)
        self._bottleApp.route('/timer/add', method="GET", callback=self._add)
        self._bottleApp.route('/server/who', method="GET", callback=self._who)
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
        broadcastSocket.sendto( bytes('rpi:room,timer\n' + str(self._roomID) + '\n' + str(self._deviceIP), 'utf-8'), ('255.255.255.255', 4000) )
    def _who(self):
        self.broadcastSelf()
        return 'broadcasting'
    def startThreaded(self):
        threading.Thread(target=self.start).start()

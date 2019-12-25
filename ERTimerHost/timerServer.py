from bottle import Bottle, route, run, template, request
import threading
class TimerServer():
    def __init__(self, timerInterface, host, port):
        self._timerSocket = timerInterface
        self._host = host
        self._port = port
        self._bottleApp = Bottle()
        self._route()
    def _route(self):
        self._bottleApp.route('/timer/status', method="GET", callback=self._status)
        self._bottleApp.route('/timer/pause', method="GET", callback=self._pause)
        self._bottleApp.route('/timer/resume', method="GET", callback=self._resume)
        self._bottleApp.route('/timer/set', method="POST", callback=self._set)
    def _status(self):
        timerState = self._timerSocket.getStatus()
        totalSeconds = timerState[0]
        timerRunning = timerState[1]
        return '{0}<br/>{1}'.format(totalSeconds, timerRunning)
    def _pause(self):
        self._timerSocket.pause()
    def _resume(self):
        self._timerSocket.resume()
    def _set(self):
        try:
            seconds = int(request.forms.get('totalseconds'))
            self._timerSocket.setSeconds(seconds)
        except ValueError:
            pass
        self._status()
    def start(self):
        self._bottleApp.run(host=self._host, port=self._port)
    def startThreaded(self):
        threading.Thread(target=self.start).start()

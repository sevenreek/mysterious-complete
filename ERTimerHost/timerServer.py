from bottle import Bottle, route, run, template

class TimerServer():
    def __init__(self, timerInterface, host, port):
        self._timerSocket = timerInterface
        self._host = host
        self._port = port
        self._bottleApp = Bottle()
        self._route()
    def _route(self):
        self._bottleApp.route('/timer/status', method="GET", callback=self._status)
    def _status(self):
        timerState = self._timerSocket.getStatus()
        totalSeconds = timerState[0]
        timerRunning = timerState[1]
        return '{0}\n{1}'.format(totalSeconds, timerRunning)
    def start(self):
        self._bottleApp.run(host=self._host, port=self._port)

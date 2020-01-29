from bottle import Bottle, route, run, template, request, response, static_file
from roomdevices import ROOMDEVICES
from roomController import RoomEvent
from CONFIGURATION import CFG_LOGS_DIR, CFG_LOGS_DATE_FORMAT
import time
import datetime
import threading
import socket
import json
import os
from logger import Logger
class TimerServer():
    BROADCAST_REPEAT_PERIOD_UNLINKED = 5
    BROADCAST_REPEAT_PERIOD_LINKED = 60
    def __init__(self, timerInterface, roomID, roomName, host, port, broadcastPort, roomController):
        self._timerSocket = timerInterface
        self._host = host
        self._port = port
        self._broadcastPort = broadcastPort
        self._roomID = roomID
        self._roomName = roomName
        self.roomctrl = roomController
        self._broadcastPeriod = self.BROADCAST_REPEAT_PERIOD_UNLINKED
        self._shouldBroadcast = False
        self._broadcastIP = '255.255.255.255'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: # try to obtain local ip of device
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            self._deviceIP = s.getsockname()[0]
            splitIP = self._deviceIP.split('.')
            #self._broadcastIP = splitIP[0] + '.' + splitIP[1] + '.255.255'
            self._broadcastIP = '<broadcast>'
            print("Running on IP: " + self._deviceIP)
            print("Broadcasting on IP: " + self._broadcastIP)
        except:
            self._deviceIP = '127.0.0.1'
        finally:
            s.close()
        self._bottleApp = Bottle()
        self._route()
        Logger.glog("Server initialized.")
    def _route(self):
        self._bottleApp.route('/timer/status', method="GET", callback=self._status)
        self._bottleApp.route('/timer/pause', method="GET", callback=self._pause)
        self._bottleApp.route('/timer/play', method="GET", callback=self._play)
        self._bottleApp.route('/timer/stop', method="GET", callback=self._stop)
        self._bottleApp.route('/timer/set', method="GET", callback=self._set)
        self._bottleApp.route('/timer/reset', method="GET", callback=self._reset)
        self._bottleApp.route('/timer/add', method="GET", callback=self._add)
        self._bottleApp.route('/link', method="GET", callback=self._link)
        self._bottleApp.route('/sudo', method="GET", callback=self._sudo)
        self._bottleApp.route('/unlink', method="GET", callback=self._unlink)
        self._bottleApp.route('/logs/<filepath>', method="GET", callback=self._servelog)
        self._bottleApp.route('/logs', method="GET", callback=self._servelog)
        self._bottleApp.route('/broadcast', method="GET", callback=self.broadcastSelf)
        self._bottleApp.route('/who', method="GET", callback=self._who)
        self._bottleApp.add_hook('after_request', func=self._enable_cors)
    def _status(self):
        jsonf = json.dumps(self.roomctrl.getState().__dict__) 
        return jsonf
    def _pause(self):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_PAUSE))
        Logger.glog("Received pause request.")
        return self._status()
    def _play(self):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_PLAY))
        Logger.glog("Received play request.")
        return self._status()
    def _stop(self):
        self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_STOP))
        Logger.glog("Received stop request.")
        return self._status()
    def _set(self):
        Logger.glog("Received set request.")
        try:
            seconds = int(request.query.get('totalseconds'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_SETTIME, seconds))
        except (ValueError, TypeError) as e:
            print(e)
            return self._status() 
        return self._status()
    def _add(self):
        Logger.glog("Received add request.")
        try:
            seconds = int(request.query.get('totalseconds'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_ADDTIME, seconds))
            return self._status()
        except (ValueError, TypeError) as e:
            print(e)
            return self._status()
    def _reset(self):
        Logger.glog("Received reset request.")
        try:
            seconds = int(request.query.get('totalseconds'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_RESET, seconds))
            return self._status()
        except (ValueError, TypeError) as e:
            print(e)
            return self._status()
    def _servelog(self, filepath=datetime.date.today().strftime(CFG_LOGS_DATE_FORMAT)):
        Logger.glog("Requested log file " + filepath)
        return static_file(filepath, Logger.instance.logsDirectory) 
    def startServer(self):
        Logger.glog("Starting server.")
        self._bottleApp.run(host=self._host, port=self._port)
    def broadcastSelf(self):
        try:
            broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            jsonFile = json.dumps(
                ( 
                self._roomName,
                self._roomID,
                ROOMDEVICES.MODEL_RPI
                )
            )
            byteSequence = bytes(jsonFile, 'utf-8') 
            broadcastSocket.sendto( byteSequence, (self._broadcastIP, self._broadcastPort) )
            broadcastSocket.close()
        except Exception as e:
            print("Broadcast failed!")
            print(e)
    def broadcastContinous(self):
        Logger.glog("Starting UDP broadcasting.")
        self._shouldBroadcast = True
        while(self._shouldBroadcast):
            self.broadcastSelf()
            time.sleep(self._broadcastPeriod)
    def _who(self):
        Logger.glog("Received /who.")
        return json.dumps(
            ( 
            self._roomName,
            self._roomID,
            ROOMDEVICES.MODEL_RPI
            )
        )
    def _link(self):
        Logger.glog("Linked.")
        self._broadcastPeriod = self.BROADCAST_REPEAT_PERIOD_LINKED
        try:
            time = request.query.get('time')
            os.system('sudo date +%T -s "{0}"'.format(time))
            print('Changed time to {0}'.format(time))
        except (ValueError, TypeError) as e:
            print(e)
            return self._status() 
        return self._status()
    def _sudo(self):
        Logger.glog("Executing arbitrary shell command.")
        try:
            cmd = request.query.get('cmd')
            print('Executing command: ' + cmd)
            os.system(cmd)
        except (ValueError, TypeError) as e:
            print(e)
            return self._status() 
        return self._status()
        self._broadcastPeriod = self.BROADCAST_REPEAT_PERIOD_LINKED    
    def _unlink(self):
        self._broadcastPeriod = self.BROADCAST_REPEAT_PERIOD_UNLINKED
    def stopBroadcast(self):
        self._shouldBroadcast = False
    def _enable_cors(self):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    def startThreaded(self):
        threading.Thread(target=self.broadcastContinous).start()
        threading.Thread(target=self.startServer).start()
    
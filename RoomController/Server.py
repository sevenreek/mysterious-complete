from bottle import Bottle, route, run, template, request, response, static_file
from roomdevices import ROOMDEVICES
from RoomControllers import DebugRoomController
from BaseRoomController import BaseRoomController
from Config import ServerConfig
import time
import datetime
import threading
import socket
import json
import os
class TimerServer():
    def __init__(self, roomController : BaseRoomController, config : ServerConfig):
        self.config = config
        self.roomctrl = roomController
        self._broadcastPeriod = self.config.STATUS_BROADCAST_REPEAT_PERIOD_UNLINKED
        self._shouldBroadcast = False
        self._broadcastIP = '<broadcast>'
        self._gameMasterIP = None
        self.linkedHostName = None
        self.deviceIP = None
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: # try to obtain local ip of device
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            self._deviceIP = s.getsockname()[0]
            splitIP = self._deviceIP.split('.')
        except:
            self._deviceIP = '127.0.0.1'
        finally:
            s.close()
        print("Running on IP: " + self._deviceIP)
        print("Broadcasting on IP: " + self._broadcastIP)
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
        self._bottleApp.route('/reboot', method="GET", callback=self._reboot)
        self._bottleApp.route('/shutdown', method="GET", callback=self._shutdown)
        self._bottleApp.route('/sudo', method="GET", callback=self._sudo)
        self._bottleApp.route('/unlink', method="GET", callback=self._unlink)
        self._bottleApp.route('/logs/<filepath>', method="GET", callback=self._servelog)
        self._bottleApp.route('/logs', method="GET", callback=self._servelog)
        self._bottleApp.route('/who', method="GET", callback=self._who)
        self._bottleApp.add_hook('after_request', func=self._enable_cors)
    def _status(self):
        statusState = {}
        jsonf = json.dumps(self.roomctrl.getState()) 
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
            seconds = int(request.query.get('t'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_SETTIME, seconds))
        except (ValueError, TypeError) as e:
            print(e)
            return self._status() 
        return self._status()
    def _add(self):
        try:
            seconds = int(request.query.get('t'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_ADDTIME, seconds))
            return self._status()
        except (ValueError, TypeError) as e:
            print(e)
            return self._status()
    def _reset(self):
        try:
            seconds = int(request.query.get('t'))
            self.roomctrl.raiseEvent(RoomEvent(RoomEvent.EVT_SERVER_RESET, seconds))
            return self._status()
        except (ValueError, TypeError) as e:
            print(e)
            return self._status()
    def _servelog(self, filepath=None):
        if (filepath is None):
            filepath = datetime.date.today().strftime(self.config.LOGS_DATE_FORMAT)
        return "Not implemented"
        #return static_file(filepath, Logger.instance.logsDirectory) 
    def startServer(self):
        self._bottleApp.run(host=self.config.HTTP_SERVER_HOST, port=self.config.HTTP_SERVER_PORT)
    def sendStatus(self, toHost, onPort):
        try:
            broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 'eth0')
            jsonFile = self._status()
            byteSequence = bytes(jsonFile, 'utf-8')
            print('Sending status to: {0}:{1}'.format(toHost, onPort))
            broadcastSocket.sendto( byteSequence, (toHost, onPort) )
            broadcastSocket.close()
        except Exception as e:
            print('exception')
            print(str(e))
    def broadcastContinous(self):
        self._shouldBroadcast = True
        while(self._shouldBroadcast):
            if(self._gameMasterIP is not None):
                self.sendStatus(self._gameMasterIP, self.config.UDP_DETECT_BROADCAST_PORT)
            else:
                self.sendStatus(self._broadcastIP, self.config.UDP_DETECT_BROADCAST_PORT)
            time.sleep(self._broadcastPeriod)
    def _who(self):
        return json.dumps(
            ( 
            self._roomName,
            self._roomID,
            ROOMDEVICES.MODEL_RPI
            )
        )
    def _link(self):
        self._broadcastPeriod = self.config.STATUS_BROADCAST_REPEAT_PERIOD_LINKED
        self._gameMasterIP = request.environ.get('REMOTE_ADDR')
        self.linkedHostName = socket.gethostbyaddr(self._gameMasterIP)
        try:
            time = request.query.get('time')
            if(time is not None):
                os.system('sudo date +%R -s "{0}"'.format(time))
        except (ValueError, TypeError) as e:
            return self._status() 
        return self._status()
    def _sudo(self):
        try:
            cmd = request.query.get('cmd')
            os.system(cmd)
        except (ValueError, TypeError) as e:
            print(e)
            return self._status() 
        return self._status()  
    def _reboot(self):
        try:
            os.system("sudo reboot")
        except Exception as e:
            print(e)
        return self._status()
    def _shutdown(self):
        try:
            os.system("sudo shutdown -h 1")
        except Exception as e:
            print(e)
        return self._status()
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
    

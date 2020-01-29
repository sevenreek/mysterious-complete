from bottle import Bottle, route, run, template, request, static_file, response
import os
from roomdevices import ROOMDEVICES
import threading
import json
from socket import socket, AF_INET, SOCK_DGRAM
import requests
from logger import Logger, CFG_LOGS_DIR, CFG_LOGS_DAYS_ARCHIVE_SIZE
import datetime
UDP_BUFFER_SIZE = 512
UDP_MESSAGE_LINE_COUNT = 3
class DeviceDetectorServer():
    def __init__(self, devices, host, port, broadcastPort):
        self._socket=socket(AF_INET, SOCK_DGRAM)
        self._socket.bind(('', broadcastPort))
        self._port = port
        self._host = host
        self._devicesIPs = devices
        self._bottleApp = Bottle()
        self._route()
        self._detectBroadcasts = False
        self._threadAlive = False
    def _route(self):
        self._bottleApp.route('/devices/list', method="GET", callback=self._list)
        self._bottleApp.route('/devices/detect', method="GET", callback=self.startThreadedDetect)
        self._bottleApp.route('/devices/halt', method="GET", callback=self.haltDetect)
        self._bottleApp.route('/admin', method="GET", callback=self._index)
        self._bottleApp.route('/<filepath:path>', callback=self._server_static)
        self._bottleApp.add_hook('after_request', func=self._enable_cors)
    def detectBroadcastContinous(self):
        self._threadAlive = True
        self._detectBroadcasts = True
        while(self._detectBroadcasts):
            try:
                packet = self._socket.recvfrom(UDP_BUFFER_SIZE)
                deviceIP = packet[1][0]
                message = packet[0].decode('utf-8')
                print("New UDP received:")
                print(message)
                deviceData = json.loads(message)
                if((deviceData[1] & 0xDE00) == 0xDE00):            
                    if(deviceIP in self._devicesIPs):
                        print('Device already known')
                    else:
                        Logger.glog("Found new device: " + str(deviceIP))
                        print('New device recognized: ' + str(deviceIP))
                        print('Linking...')
                        requests.get(url = 'http://' + str(deviceIP) + ':' + str(self._port) + '/link?time=' + datetime.datetime.now().strftime('%T')) 
                        self._devicesIPs.append(deviceIP)
            except Exception as e:
                print('Error while processing UDP broadcast.')
                print(e)
        self._threadAlive = False
    def startCommunicationServer(self):
        self._bottleApp.run(host=self._host, port=self._port)
    def startThreadedDetect(self):
        if(not self._threadAlive):
            threading.Thread(target=self.detectBroadcastContinous).start()
    def haltDetect(self):
        self._detectBroadcasts = False
    def _list(self):
        json_out = json.dumps(self._devicesIPs)
        print(json_out)
        return json_out
    def _index(self):
        return self._server_static('index.html')
    def _server_static(self, filepath):
        directory = os.path.join(os.path.dirname(__file__), '..', 'ERAdmin')
        return static_file(filepath, directory)
    def _enable_cors(self):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
if __name__ == "__main__":
    devices = []
    l = Logger(CFG_LOGS_DIR, CFG_LOGS_DAYS_ARCHIVE_SIZE)
    l.makeGlobal
    server = DeviceDetectorServer(devices, 'localhost', 8080, 4000)
    server.startThreadedDetect()
    server.startCommunicationServer()
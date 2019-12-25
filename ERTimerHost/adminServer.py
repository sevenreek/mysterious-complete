from bottle import Bottle, route, run, template, request
from roomdevices import ROOMDEVICES
import threading
from socket import socket, AF_INET, SOCK_DGRAM
UDP_BUFFER_SIZE = 512
UDP_MESSAGE_LINE_COUNT = 4
class DeviceDetectorServer():
    def __init__(self, unlinkedIPs, host, port, broadcastPort):
        self._socket=socket(AF_INET, SOCK_DGRAM)
        self._socket.bind(('', broadcastPort))
        self._port = port
        self._host = host
        self._unlinkedDevicesIPs = unlinkedIPs
        self._bottleApp = Bottle()
        self._route()
        self._detectBroadcasts = False
        self._threadAlive = False
    def _route(self):
        self._bottleApp.route('/devices/list', method="GET", callback=self._list)
        self._bottleApp.route('/devices/detect', method="GET", callback=self.startThreadedDetect)
        self._bottleApp.route('/devices/halt', method="GET", callback=self.haltDetect)
        self._bottleApp.route('/admin/hello', method="GET", callback=self._hello)
    def detectBroadcastContinous(self):
        self._threadAlive = True
        self._detectBroadcasts = True
        while(self._detectBroadcasts):
            packet = self._socket.recvfrom(UDP_BUFFER_SIZE)
            deviceIP = packet[1]
            message = packet[0].decode('utf-8')
            splitMsg = message.split('\n') # change this when moved to JSONs
            if(len(splitMsg) == UDP_MESSAGE_LINE_COUNT and splitMsg[0] in ROOMDEVICES.MODELS):
                if(deviceIP in self._unlinkedDevicesIPs):
                    print('broadcast from detected device')
                else:
                    print('found new device')
                    self._unlinkedDevicesIPs.append(deviceIP)
        self._threadAlive = False
    def startCommunicationServer(self):
        self._bottleApp.run(host=self._host, port=self._port)
    def startThreadedDetect(self):
        if(not self._threadAlive):
            threading.Thread(target=self.detectBroadcastContinous).start()
    def haltDetect(self):
        self._detectBroadcasts = False
    def _list(self):
        response = ''
        for ip in self._unlinkedDevicesIPs: # append all unlinked ips to string
            response = response + ip + '\n'
        return response[:-1] # strip last \n
    def _hello(self):
        return 'detector operating'
if __name__ == "__main__":
    unlinkedIPs = []
    server = DeviceDetectorServer(unlinkedIPs, 'localhost', 8080, 4000)
    server.startThreadedDetect()
    server.startCommunicationServer()
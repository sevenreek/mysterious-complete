import requests
import socket
import threading
from config import Config, AlertConfig
import json
import datetime
from queue import Queue
class Device():
    def __init__(self, ip : str, name : str, did : int, timeleft = None, state = None, startedon = None, components = {}):
        self.ip = ip
        self.name = name
        self.id = did
        self.timeleft = timeleft
        self.state = state
        self.startedon = startedon
        self.alerts = Queue(maxsize=16)
        self.components  = components
    def getBasicStatusDictionary(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'timeleft' : self.timeleft,
            'state' : self.state,
            'alertcount' : self.alerts.qsize()
        }
    def appendAlert(self, alert):
        for a in self.alerts:
            if a[0] == alert[0]:
                return False
        self.alerts.put(alert)
        return True
class BasicDeviceEncoder(json.JSONEncoder):
    def default(self, o):
            return o.getBasicStatusDictionary()    
class DevicesCommunicationServer():
    def __init__(self, config : Config, alertConfig : AlertConfig):
        self.useTCPPolling = config.DEVICESERVER_USE_TCP_UPDATE
        self.udpPort = config.DEVICESERVER_UDP_PORT
        self.tcpPort = config.DEVICESERVER_TCP_PORT
        self.bufferSize = config.DEVICESERVER_UDP_BUFFER
        self.deviceMask = config.DEVICE_MASK
        self.alertConfig = alertConfig
        self.threadAlive = False
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind(('', self.udpPort))
        self.detectedDevices = []
    def run(self):
        self.threadAlive = True
        while(self.threadAlive):
            try:
                if self.useTCPPolling:
                   self.tcpPollDevices()
                packet = self.serverSocket.recvfrom(self.bufferSize)    
                deviceIP = packet[1][0]
                message = packet[0].decode('utf-8')
                print(message)
                try:
                    deviceDataRaw = json.loads(message)
                    deviceData = Device(
                        ip = deviceIP, 
                        name = deviceDataRaw['name'],
                        did = deviceDataRaw['id'],
                        timeleft = deviceDataRaw['timeleft'],
                        state = deviceDataRaw['state'])
                    if((deviceData.id & self.deviceMask) == self.deviceMask):
                        deviceKnown = False
                        for deviceIndex in range(len(self.detectedDevices)):
                            if(self.detectedDevices[deviceIndex].id == deviceData.id):
                                self.detectedDevices[deviceIndex] = deviceData
                                deviceKnown = True
                        if not deviceKnown:
                            print('New device recognized. Syncing time.')
                            r = requests.get(url = 'http://' + str(deviceIP) + ':' + str(self.tcpPort) + '/link?time=' + datetime.datetime.now().strftime('%R')) 
                            try:
                                r.raise_for_status()
                            except requests.exceptions.HTTPError as e:
                                deviceData.appendAlert(self.alertConfig.ERROR_HTTP_LINK_FAILED)
                                print(e)
                            self.detectedDevices.append(deviceData)
                except (json.JSONDecodeError, KeyError) as e:
                    print(e)
            except Exception as e:
                print(e)
    def runThreaded(self):
        threading.Thread(target=self.run).start()
    def sendCommand(self, device, command):
        pass
    def tcpPollDevices(self):
        for device in self.detectedDevices:
            response = requests.get(url = 'http://' + str(device.ip) + ':' + str(self._port) + '/status') 
            jsonData = response.json()
            device.timeleft = jsonData['timeleft']
            device.status = jsonData['status']



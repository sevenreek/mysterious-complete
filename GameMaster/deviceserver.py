import requests
import socket
import threading

from config import Config, AlertConfig
import json
import datetime
from queue import Queue
class Device():
    def __init__(self, ip : str, name : str, did : int, timeleft = None, linkedIP=None, state = None, startedon = None, components = {}):
        self.ip = ip
        self.name = name
        self.id = did
        self.timeleft = timeleft
        self.state = state
        self.startedon = startedon
        self.alerts = Queue(maxsize=16)
        self.linkedToIP = linkedIP
        self.lastStatus = None
        self.components  = components
    def getBasicStatusDictionary(self):
        if(self.lastStatus is not None):
            lastReceivedPacketDiff = self.lastStatus - datetime.datetime.now()
        else:
            lastReceivedPacketDiff = None
        return {
            'id' : self.id,
            'name' : self.name,
            'ip' : self.ip,
            'gm' : self.linkedToIP,
            'timeleft' : self.timeleft,
            'state' : self.state,
            'updatedago' : lastReceivedPacketDiff
            'alertcount' : self.alerts.qsize()
        }
    def appendAlert(self, alert):
        self.alerts.put(alert)
        return True
    def updateStatus(self):
        self.lastStatus = datetime.datetime.now()
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
                packet = self.serverSocket.recvfrom(self.bufferSize) # recieve packet
                deviceIP = packet[1][0]
                message = packet[0].decode('utf-8')
                try:
                    deviceJSON = json.loads(message)
                    deviceData = self.deviceFromDict(jsonstr=deviceJSON, deviceIP=deviceIP)
                    if((deviceData.id & self.deviceMask) == self.deviceMask):
                        deviceKnown = self.checkIfDeviceIsKnown(deviceData)
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect((deviceIP, 8080))
                        hostIP = s.getsockname()[0]
                        if not deviceKnown:
                            print('Unlinked device recognized. Syncing time.')
                            self.linkDevice(device=deviceData, ip=deviceIP)
                            self.detectedDevices.append(deviceData)
                        elif deviceData.linkedToIP != hostIP:
                            print('Wrongly linked device recognized. Syncing time.')
                            self.linkDevice(device=deviceData, ip=deviceIP)
                except (json.JSONDecodeError, KeyError) as e:
                    print(e)
            except Exception as e:
                print(e)
    def runThreaded(self):
        threading.Thread(target=self.run).start()
    def sendCommand(self, device, command):
        response = requests.get(url = 'http://' + str(device.ip) + ':' + str(self._port) + '/status') 
    def tcpPollDevices(self):
        for device in self.detectedDevices:
            response = requests.get(url = 'http://' + str(device.ip) + ':' + str(self._port) + '/status') 
            jsonData = response.json()
            device.timeleft = jsonData['timeleft']
            device.status = jsonData['status']
    def deviceFromDict(self, jsonstr, deviceIP) -> Device:
        return Device(
            ip = deviceIP, 
            name = jsonstr['name'],
            did = jsonstr['id'],
            timeleft = jsonstr['timeleft'],
            state = jsonstr['state'], 
            linkedIP = jsonstr['gm'])
    def checkIfDeviceIsKnown(self, device : Device) -> bool:
        deviceKnown = False
        for deviceIndex in range(len(self.detectedDevices)):
            if(self.detectedDevices[deviceIndex].id == device.id):
                self.detectedDevices[deviceIndex] = device
                device.updateStatus()
                deviceKnown = True
                break
        return deviceKnown
    def linkDevice(self, device : Device, ip: str) -> bool:
        r = requests.get(url = 'http://' + str(ip) + ':' + str(self.tcpPort) + '/link?time=' + datetime.datetime.now().strftime('%R')) 
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            device.appendAlert(self.alertConfig.ERROR_HTTP_LINK_FAILED)
            print(e)
            return False
        return True
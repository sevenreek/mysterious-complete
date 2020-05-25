import requests
import socket
import threading
from config import Config
import json
import datetime
from typing import Callable
class Room():
    def __init__(self, ip: str, name: str, room_id: int, timeleft=None, linked_ip=None, state=None, started_on=None, components=[]):
        self.ip = ip
        self.name = name
        self.room_id = room_id
        self.timeleft = timeleft
        self.state = state
        self.started_on = started_on
        self.linked_ip = linked_ip
        self.last_status = None
        self.components  = components
    def on_room_update(self):
        self.last_status = datetime.datetime.now()
    @classmethod
    def from_json(cls, jsonstr, ip):
        return Room(
            ip=ip, 
            name=jsonstr['name'],
            room_id=jsonstr['id'],
            linked_ip=jsonstr['linked_to'])
    def update_json(self, **kwargs):
        self.on_room_update()
        self.__dict__.update(
            (k, v) for k, v in kwargs.items() 
            if k in self.__dict__.keys()    # update only fields that already exist
        )
class RoomOverviewEncoder(json.JSONEncoder):
    def default(self, o:Room):
            return {
                "ip": o.ip,
                "name": o.name,
                "id": o.room_id,
                "timeleft": o.timeleft,
                "started_on": o.started_on,
                "state": o.state,
                "last_status": o.last_status,
            }    
class DevicesCommunicationServer():
    def __init__(self, config: Config):
        self.lock = threading.Lock()
        self.useTCPPolling = config.DEVICESERVER_USE_TCP_UPDATE
        self.udpPort = config.DEVICESERVER_UDP_PORT
        self.tcpPort = config.DEVICESERVER_TCP_PORT
        self.bufferSize = config.DEVICESERVER_UDP_BUFFER
        self.roomMask = config.DEVICE_MASK
        self.threadAlive = False
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind(('', self.udpPort))
        self.detectedDevices = []
        self.rooms = []
    def run(self):
        self.threadAlive = True
        while(self.threadAlive):
            try:
                packet = self.serverSocket.recvfrom(self.bufferSize) # recieve packet
                room_IP = packet[1][0]
                message = packet[0].decode('utf-8')
                try:
                    room_JSON = json.loads(message)
                    self.handle_room_update(room_JSON, room_IP)
                except (json.JSONDecodeError, KeyError) as e:
                    print("Exception from deviceserver")
                    print(e)
            except Exception as e:
                print(e)

    def runThreaded(self):
        threading.Thread(target=self.run).start()

    def sendCommand(self, deviceIndex, command):
        response = requests.get(url = 'http://' + str(self.rooms[deviceIndex].ip) + ':' + str(self.tcpPort) + '/' + command) 

    def getupdate_room(self, room_JSON) -> Room:
        for room in self.rooms:
            if(room.id == room_JSON['room_id']):
                with self.lock:
                    room.update_json(room_JSON)
                return room
        return None
    def link_room(self, ip: str) -> bool:
        r = requests.get(url = 'http://' + str(ip) + ':' + str(self.tcpPort) + '/link?time=' + datetime.datetime.now().strftime('%R')) 
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            return False
        return True
    def handle_room_update(self, room_JSON, room_IP):
        linked_to = room_JSON['linked_to']  
        if((room_JSON['room_id'] & self.roomMask) == self.roomMask):
            found_room = self.getupdate_room(room_JSON)
            if found_room is None:
                print('Unlinked device recognized. Syncing time.')
                found_room = Room.from_json(room_JSON)
                self.link_room(ip=room_IP)
                with self.lock:
                    self.rooms.append(found_room)
            elif room_JSON['linked_to'] != self.get_this_IP(room_IP):
                print('Wrongly linked device recognized. Syncing time.')
                self.link_room(ip=room_IP)
    def get_this_IP(self, network_IP) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((network_IP, self.tcpPort))
        ip = s.getsockname()[0]
        s.close()
        return ip
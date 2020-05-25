from bottle import Bottle, route, run, template, request, response, static_file
from RoomControllers import DebugRoomController
from BaseRoomController import BaseRoomController
from Room import ServerConfig
from GameEvents import BaseGameEvents, GameEvent
import time
import datetime
import threading
import socket
import json
import os
from room_app.game_context import ServerData, GameComponent
class BaseServer(GameComponent):
    def __init__(self, config:ServerConfig, context_manager):
        self.config = config
        self.broadcast_period = self.config.STATUS_BROADCAST_REPEAT_PERIOD_UNLINKED
        self.default_port = self.config.UPDATE_PORT
        self.should_broadcast = False
        self.broadcast_IP = '<broadcast>'
        self.context_manager = context_manager
        self.linked_to = None
        self.IP = self.get_local_IP('10.255.255.255')
        print("Running on IP: " + self.IP)
        print("Broadcasting on IP: " + self.IP)
        self.bottle_app = Bottle()
        self.bottle_app.add_hook('after_request', func=self.enable_cors)
    #begin GameComponent override
    NAME = ServerData.NAME
    def get_component_data(self):
        return ServerData(
            ip=self.IP,
            linked_to=self.linked_to,
        ) 
    #end GameComponent override
    def start_HTTP_server(self):
        self.bottle_app.run(host=self.config.HTTP_SERVER_HOST, port=self.config.HTTP_SERVER_PORT)
    def send_data(self, data, on_port=self.default_port, to_address=self.linked_to):
        if(to_address is None):
            used_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            used_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            to_address = self.broadcast_address
        else:
            used_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            data_as_bytes = bytes(json.dumps(data), 'utf-8')
            print('Sending update to: {0}:{1}'.format(to_address, on_port))
            used_socket.sendto( data_as_bytes, (to_address, on_port) )
            used_socket.close()
        except Exception as e:
            print(str(e))
    def broadcast_continuous(self):
        self.should_broadcast = True
        while(self.should_broadcast):
            self.send_data(self.context_manager[ServerData.NAME].get_tuple())
            time.sleep(self.broadcast_period)
    def stop_broadcast(self):
        self.should_broadcast = False
    def enable_cors(self):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    def start_threaded(self):
        #threading.Thread(target=self.broadcastContinous).start()
        threading.Thread(target=self.start_HTTP_server).start()
    @classmethod
    def get_local_IP(cls, using_host):
        IP = None
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: # try to obtain local ip of device
            # doesn't even have to be reachable
            s.connect((using_host, 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP



from enum import Enum
from abc import ABCMeta, abstractmethod
class ContextManager(dict):
    def __init__(self):
        self.components = {}
    def __getitem__(self, key):
        return self.components[key].get_component_data()
    def __setitem__(self, key, value):
        self.components[key] = value
    def append_component(self, component: GameComponent):
        self.components[component.NAME] = component

class GameComponent(metaclass=ABCMeta):
    NAME = NotImplementedError("GameComponent must override NAME static parameter") 
    @abstractmethod
    def get_component_data(self) -> GameComponentData:
        raise NotImplementedError('get_component_data not implemented')

class GameComponentData():
    NAME = NotImplementedError("GameComponentData must override NAME static parameter")
    def get_tuple(self):
        return (self.NAME, vars(self))

class TimerData(GameComponentData):
    NAME = 'timer'
    def __init__(self, seconds_left: int, counting_down: bool):
        self.seconds_left = seconds_left
        self.counting_down = counting_down

class ServerData(GameComponentData):
    NAME = 'server'
    def __init__(self, ip: str, linked_to: str):
        self.ip = ip
        self.linked_to = linked_to

class GAMESTATES(Enum):
    READY = 0
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3

class GameData(GameComponentData):
    NAME = 'game'
    def __init__(self, room_id: int, room_name: str, started_on, state: GAMESTATES):
        self.room_id = room_id
        self.room_name = room_name
        self.started_on = started_on
        self.state = state
        


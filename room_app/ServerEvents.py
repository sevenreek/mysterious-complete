import bottle

class SimpleSEH(): # Server Event Handler
    NAME = 'default'
    def handle(self, command: str, param=None):
        raise NotImplementedError(f"Cannot use base ServerEventHandler for {self.NAME}")
    def register(self, bottle_app: bottle.Bottle, methods):
        bottle_app.route(f'/{self.NAME}/<command>/<param>', method=methods, callback=lambda command, param: self.handle(command, param))
        bottle_app.route(f'/{self.NAME}/<command>/', method=methods, callback=lambda command: self.handle(command))

class ComplexSEH():
    NAME = 'default'
    def handle(self, command: str, request_obj: bottle.Request):
        raise NotImplementedError(f"Cannot use base ServerEventHandler for {self.NAME}")
    def register(self, bottle_app: bottle.Bottle, methods):
        bottle_app.route(f'/{self.NAME}/<command>', method=methods, callback=lambda command: self.handle(command, bottle.request))

class TimerSEH(SimpleSEH):
    NAME = 'timer'
    def __init__(self, timer,  ):
        self.function_lookup = {
            'add': self.__add,
            'set': self.__set,
        }
        self.timer = timer
    def handle(self, command: str, param=None):
        if(param is not None):
            try: param = int(param)
            except: print(f"Parameter for {command} of {self.NAME} must be int.")    
        try:
            self.function_lookup[str](param)
        except KeyError as e:
            print(f"Command {command} is not registered to component {self.NAME}.")
    def __add(self, param):
        self.timer
    def __set(self, param):
        pass
class GameSEH(SimpleSEH):
    NAME = 'game'
    def __init__(self):
        self.function_lookup = {
            'pause': self.__pause,
            'stop': self.__stop,
            'play': self.__play,
            'reset': self.__reset,
        }
    def handle(self, command: str, param=None):
        if(param is not None):
            try: param = int(param)
            except: print(f"Parameter for {command} of {self.NAME} must be int.")    
        try:
            self.function_lookup[str](param)
        except KeyError as e:
            print(f"Command {command} is not registered to component {self.NAME}.")
    def __pause(self, param):
        pass
    def __stop(self, param):
        pass
    def __play(self, param):
        pass
    def __reset(self, param):
        pass
class BasicServerRouteStrategy():
    def __init__(self, server: TimerServer, bottle_app: bottle.Bottle):
        self.server = server
        self.bottle_app = bottle_app
    def register_handler(self, component_name: str, handler: ServerEventHandler):
        self.bottle_app.route()
    def route(self, ):
        a.route('/', method="GET", callback=self.status)
        a.route('/timer/<command:path>', method="GET", callback=self.pause)
        a.route('/timer/play', method="GET", callback=self.play)
        a.route('/timer/stop', method="GET", callback=self.stop)
        a.route('/timer/set/<t>', method="GET", callback=self.settime)
        a.route('/timer/reset/<t>', method="GET", callback=self.reset)
        a.route('/timer/add/<t>', method="GET", callback=self.addtime)
        a.route('/rpilink', method="GET", callback=self.link)
        a.route('/reboot', method="GET", callback=self.reboot)
        a.route('/shutdown', method="GET", callback=self.shutdown)
        a.route('/sudo', method="GET", callback=self.sudo)
        a.route('/unlink', method="GET", callback=self.unlink)
    def status(self):
        statusState = {}
        jsonf = json.dumps(self.roomctrl.getState()) 
        return jsonf
    def pause(self):
        self.roomctrl.raiseEvent(GameEvent(BaseGameEvents.SERVER_PAUSE))
        return self._status()
    def play(self):
        self.roomctrl.raiseEvent(GameEvent(BaseGameEvents.SERVER_PLAY))
        return self._status()
    def stop(self):
        self.roomctrl.raiseEvent(GameEvent(BaseGameEvents.SERVER_STOP))
        return self._status()
    def settime(self, t=None):
        try:
            seconds = int(request.query.get('t'))
            self.roomctrl.raiseEvent(GameEvent(BaseGameEvents.SERVER_SETTIME, t))
        except (ValueError, TypeError) as e:
            print(e)
            return self._status() 
        return self._status()
    def addtime(self, t=None):
        try:
            seconds = int(request.query.get('t'))
            self.roomctrl.raiseEvent(GameEvent(BaseGameEvents.SERVER_ADDTIME, seconds))
            return self._status()
        except (ValueError, TypeError) as e:
            print(e)
            return self._status()
    def reset(self, t=None):
        try:
            seconds = int(request.query.get('t'))
            self.roomctrl.raiseEvent(GameEvent(BaseGameEvents.SERVER_RESET, seconds))
            return self._status()
        except (ValueError, TypeError) as e:
            print(e)
            return self._status()
    def link(self):
        self._broadcastPeriod = self.config.STATUS_BROADCAST_REPEAT_PERIOD_LINKED
        self._gameMasterIP = request.environ.get('REMOTE_ADDR')
        try:
            time = request.query.get('time')
            if(time is not None):
                os.system('sudo date +%R -s "{0}"'.format(time))
        except (ValueError, TypeError) as e:
            return self._status() 
        return self._status()
    def sudo(self):
        try:
            cmd = request.query.get('cmd')
            os.system(cmd)
        except (ValueError, TypeError) as e:
            print(e)
            return self._status() 
        return self._status()  
    def reboot(self):
        try:
            os.system("sudo reboot")
        except Exception as e:
            print(e)
        return self._status()
    def shutdown(self):
        try:
            os.system("sudo shutdown -h 1")
        except Exception as e:
            print(e)
        return self._status()
    def unlink(self):
        self._broadcastPeriod = self.BROADCAST_REPEAT_PERIOD_UNLINKED
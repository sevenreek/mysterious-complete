import room_app.game_context as game_context

class Game(game_context.GameComponent):
    NAME = NotImplementedError("GameComponent must override NAME static parameter")
    @abstractmethod
    def get_component_data(self) -> GameComponentData:
        raise NotImplementedError('get_component_data not implemented')
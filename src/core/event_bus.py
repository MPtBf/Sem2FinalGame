from enum import Enum, auto


class EventType(Enum):
    ENEMY_SPAWN = auto()
    ENEMY_DEATH = auto()
    ENEMY_DAMAGE = auto()

    PLAYER_DEATH = auto()
    PLAYER_DAMAGE = auto()
    PLAYER_COLLECT_RESOURCES = auto()

    DRILL_DEATH = auto()
    DRILL_DAMAGE = auto()


class EventBus:
    def __init__(self):
        # ключ - тип события, значение - список слушателей
        self._listeners = {}

    def subscribe(self, event_name, callback):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name, **kwargs):
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(**kwargs)

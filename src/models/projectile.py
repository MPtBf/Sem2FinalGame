
from models.game_object import DynamicObject


class Projectile(DynamicObject):
    def __init__(self, pos: pg.Vector2, type: ObjectType, velocity: pg.Vector2):
        super().__init__(pos, type, velocity)

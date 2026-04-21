
from models.entity import Entity


class Bullet(Entity):
    def __init__(self, pos: pg.Vector2, velocity: pg.Vector2, health: float, rect: pg.Rect):
        super().__init__(pos, velocity, health, rect)
        ...
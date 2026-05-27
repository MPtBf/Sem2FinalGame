import pygame as pg
from src.models.game_object import DynamicObject, ObjectType
from src.core.config import PROJECTILE_INHERIT_PLAYER_VELOCITY, PROJECTILE_SIZE, PROJECTILE_SPEED, PROJECTILE_LIFETIME


class Projectile(DynamicObject):
    def __init__(self, pos: pg.Vector2, direction: pg.Vector2, shooter_velocity: pg.Vector2 = None):
        size = pg.Vector2(*PROJECTILE_SIZE)
        base = direction.normalize() * PROJECTILE_SPEED if direction.length() > 0 else pg.Vector2(1, 0) * PROJECTILE_SPEED
        if shooter_velocity is None:  shooter_velocity = pg.Vector2(0, 0)
        velocity = base + shooter_velocity * PROJECTILE_INHERIT_PLAYER_VELOCITY
        super().__init__(pos, size, ObjectType.PROJECTILE, velocity)
        self.alive = True
        self._lifetime = PROJECTILE_LIFETIME

    def update_logic(self, dt, world, intents=None):
        self._lifetime -= dt
        if self._lifetime <= 0:
            self.die()

    def die(self):
        self.alive = False

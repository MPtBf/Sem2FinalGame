
import pygame as pg
from models.game_object import DynamicObject, ObjectType
from src.core.config import PROJECTILE_SIZE


class Projectile(DynamicObject):
    def __init__(self, pos: pg.Vector2, object_type: ObjectType, velocity: pg.Vector2):
        size = pg.Vector2(*PROJECTILE_SIZE)
        super().__init__(pos, size, object_type, velocity)

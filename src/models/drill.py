import pygame as pg
from .game_object import LivingEntity, ObjectType

class Drill(LivingEntity):
    def __init__(self, pos: pg.Vector2, health):
        super().__init__(pos, ObjectType.DRILL, health)
        self.storage = {}

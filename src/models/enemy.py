import pygame as pg
from .game_object import LivingEntity, ObjectType
from src.core.config import ENEMY_SIZE, ENEMY_HEALTH

class Enemy(LivingEntity):
    def __init__(self, pos: pg.Vector2):
        super().__init__(
            pos, 
            pg.Vector2(*ENEMY_SIZE), 
            ObjectType.ENEMY, 
            ENEMY_HEALTH
        )

    def update_logic(self, dt, world, intents=None):
        ...

    def die(self):
        ...

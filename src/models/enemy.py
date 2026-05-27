import pygame as pg
from .game_object import LivingEntity, ObjectType
from src.core.config import ENEMY_SIZE, ENEMY_HEALTH, ENEMY_CONTACT_DAMAGE, ENEMY_DAMAGE_COOLDOWN

class Enemy(LivingEntity):
    def __init__(self, pos: pg.Vector2):
        super().__init__(
            pos, 
            pg.Vector2(*ENEMY_SIZE), 
            ObjectType.ENEMY, 
            ENEMY_HEALTH
        )
        self._damage_cooldown = 0.0

    def update_logic(self, dt, world, intents=None):
        if self._damage_cooldown > 0:
            self._damage_cooldown -= dt

    def try_damage(self, target):
        if self._damage_cooldown <= 0:
            target.take_damage(ENEMY_CONTACT_DAMAGE)
            self._damage_cooldown = ENEMY_DAMAGE_COOLDOWN
            return True
        return False

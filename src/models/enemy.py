import pygame as pg
from .game_object import LivingEntity, ObjectType
from src.settings.balance import ENEMY_HEALTH, ENEMY_CONTACT_DAMAGE, ENEMY_DAMAGE_COOLDOWN, ENEMY_FRICTION
from src.settings.visual import ENEMY_SIZE

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
        super().update_logic(dt, world, intents)
        if self._damage_cooldown > 0:
            self._damage_cooldown -= dt
        
        # apply friction to slow down if pushed by projectile
        self.velocity *= (1 - ENEMY_FRICTION)

    def try_damage(self, target, knockback_direction: pg.Vector2 = None):
        if self._damage_cooldown <= 0:
            target.take_damage(ENEMY_CONTACT_DAMAGE, knockback_direction)
            self._damage_cooldown = ENEMY_DAMAGE_COOLDOWN
            return True
        return False

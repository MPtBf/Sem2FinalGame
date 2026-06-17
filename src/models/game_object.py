import pygame as pg
from enum import Enum, auto
from src.settings.base import ObjectType
from src.settings.balance import ENTITY_WEIGHT_MAP, KNOCKBACK_FORCE, VELOCITY_LOSS_ON_HIT
from src.settings.visual import Z_INDEX, HP_BAR_FLASH_DURATION


class GameObject:
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, object_type: ObjectType):
        self._pos = pg.Vector2(pos)
        self._size = pg.Vector2(size)
        self._rect = pg.Rect(self._pos.x, self._pos.y, self._size.x, self._size.y)
        self.object_type = object_type
        self.z_index = Z_INDEX[object_type]
        self.is_visible = True
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        self._pos = pg.Vector2(value)
        self._rect.topleft = (self._pos.x, self._pos.y)
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = pg.Vector2(value)
        self._rect.size = (self._size.x, self._size.y)
    
    @property
    def rect(self):
        return self._rect

    def sync_rect_to_pos(self):
        """updates rect integer coordinates from float pos"""
        self._rect.x = round(self._pos.x)
        self._rect.y = round(self._pos.y)

    def sync_pos_to_rect(self):
        """updates float pos from rect integer coordinates
        (after collision)"""
        self._pos.x = self._rect.x
        self._pos.y = self._rect.y

    def delete(self):
        ...


class DynamicObject(GameObject):
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, object_type: ObjectType, velocity: pg.Vector2):
        super().__init__(pos, size, object_type)
        self.velocity = velocity
    
    def move_x(self, dt):
        self._pos.x += self.velocity.x * dt
        self.sync_rect_to_pos()

    def move_y(self, dt):
        self._pos.y += self.velocity.y * dt
        self.sync_rect_to_pos()

    def update_logic(self, dt, world, intents=None):
        """internal logic:  ai, input handling, velocity updates"""
        ...

    def after_move(self, axis, world):
        """called after each axis movement inside collision handling"""
        ...

class LivingEntity(DynamicObject):
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, object_type: ObjectType, health):
        super().__init__(pos, size, object_type, velocity=pg.Vector2(0,0))
        self.max_health = health
        self.health = health
        self._damage_flash_timer = 0.0
    
    def update_logic(self, dt, world, intents=None):
        super().update_logic(dt, world, intents)
        if self._damage_flash_timer > 0:
            self._damage_flash_timer -= dt
    
    def take_damage(self, amount, knockback_direction: pg.Vector2 = None):
        self.health -= amount
        self._damage_flash_timer = HP_BAR_FLASH_DURATION
        self._apply_knockback(knockback_direction)
        if self.health <= 0:
            self.die()

    def _apply_knockback(self, knockback_direction):
        if knockback_direction is not None and knockback_direction.length() > 0:
            self.velocity *= VELOCITY_LOSS_ON_HIT
            kb_mult = KNOCKBACK_FORCE / ENTITY_WEIGHT_MAP[self.object_type]  # more weight -> less knockback
            self.velocity += knockback_direction.normalize() * kb_mult

    def is_alive(self):
        return self.health > 0

    def die(self):
        pass

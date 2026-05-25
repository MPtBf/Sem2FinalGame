import pygame as pg
from enum import Enum, auto
from src.core.config import Z_INDEX, ObjectType


class GameObject:
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, object_type: ObjectType):
        self._pos = pg.Vector2(pos)
        self._size = pg.Vector2(size)
        self._rect = pg.Rect(self._pos.x, self._pos.y, self._size.x, self._size.y)
        self.object_type = object_type
        self.z_index = Z_INDEX[object_type]
    
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

    def update(self, dt):
        # EXPLAIN ME
        self.move_x(dt)
        self.move_y(dt)


class LivingEntity(DynamicObject):
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, object_type: ObjectType, health):
        super().__init__(pos, size, object_type, velocity=pg.Vector2(0,0))
        self.health = health
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        pass

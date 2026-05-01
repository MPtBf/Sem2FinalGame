from abc import ABC
import pygame as pg
from enum import Enum, auto
from src.core.config import Z_INDEX, ObjectType


class GameObject:
    def __init__(self, pos: pg.Vector2, object_type: ObjectType):
        self.pos = pos
        self.object_type = object_type
        self.z_index = Z_INDEX[object_type]


class DynamicObject(GameObject):
    def __init__(self, pos: pg.Vector2, object_type: ObjectType, velocity: pg.Vector2):
        super().__init__(pos, object_type)
        self.velocity = velocity
    
    def update(self, dt):
        self.pos += self.velocity * dt


class LivingEntity(DynamicObject):
    def __init__(self, pos: pg.Vector2, object_type: ObjectType, health):
        super().__init__(pos, object_type, velocity=pg.Vector2(0,0))
        self.health = health
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        pass

from abc import ABC, abstractmethod

import pygame as pg
from src.settings.base import ObjectType
from src.settings.balance import ENTITY_WEIGHT_MAP, KNOCKBACK_FORCE, VELOCITY_LOSS_ON_DAMAGE


class GameObject(ABC):
    """базовый класс для всех объектов в игре"""

    def __init__(self, pos: pg.Vector2, size: pg.Vector2, object_type: ObjectType):
        self._pos = pg.Vector2(pos)
        self._size = pg.Vector2(size)
        self._rect = pg.Rect(self._pos.x, self._pos.y, self._size.x, self._size.y)
        self.object_type = object_type
    
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


class DynamicObject(GameObject):
    """базовый класс для всех подвижных объектов в игре. Скорость, ускорение"""
    
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, object_type: ObjectType, velocity: pg.Vector2):
        super().__init__(pos, size, object_type)
        self._velocity = velocity
        self._acceleration = pg.Vector2(0, 0)

    @property
    def velocity(self):
        return self._velocity
    
    @property
    def acceleration(self):
        return self._acceleration
    
    def move_x(self, dt):
        self._pos.x += self._velocity.x * dt
        self.sync_rect_to_pos()

    def move_y(self, dt):
        self._pos.y += self._velocity.y * dt
        self.sync_rect_to_pos()

    def sync_rect_to_pos(self) -> None:
        """Обновляет rect целые координаты из дробного pos вектора"""
        self._rect.x = round(self._pos.x)
        self._rect.y = round(self._pos.y)

    def sync_pos_to_rect(self) -> None:
        """Обновляет pos вектор из целых координат rect"""
        self._pos.x = self._rect.x
        self._pos.y = self._rect.y

    @abstractmethod
    def update_logic(self, dt, world, intents=None):
        """внутрянняя логика:  ИИ, обновления интентов, обновления скорости"""
        pass

    def after_move(self, axis, world):
        """вызывается после каждого перемещения по оси внутри обработки столкновений"""
        pass

class LivingEntity(DynamicObject):
    """базовый класс для всех живых сущностей в игре. Урон, отдача"""
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, object_type: ObjectType, health):
        super().__init__(pos, size, object_type, velocity=pg.Vector2(0,0))
        self.max_health = health
        self.health = health
        self.time_from_last_damage = float('inf')
    
    def update_logic(self, dt, world, intents=None):
        super().update_logic(dt, world, intents)
        self.time_from_last_damage += dt
    
    def take_damage(self, amount, knockback_direction: pg.Vector2 = None):
        """получение урон. Обновляет скорость, здоровье, применяет отдачу"""
        self._velocity *= (1 - VELOCITY_LOSS_ON_DAMAGE)
        self.health -= amount
        self.time_from_last_damage = 0
        self.apply_knockback(knockback_direction)
        if self.health <= 0:
            self.die()

    def apply_knockback(self, knockback_direction, force=None):
        """принимает отдачу. Обновляет скорость"""
        if force is None:
            force = KNOCKBACK_FORCE

        if knockback_direction is not None and knockback_direction.length() > 0:
            kb_mult = force / ENTITY_WEIGHT_MAP[self.object_type]  # more weight -> less knockback
            self._velocity += knockback_direction.normalize() * kb_mult

    def is_alive(self):
        return self.health > 0

    @abstractmethod
    def die(self):
        pass

from abc import ABC
import pygame as pg

class Entity(ABC):
    def __init__(
            self,
            pos: pg.Vector2,
            velocity: pg.Vector2,
            health: float,
            size: tuple,
        ):
        self.pos = pos
        self.velocity = velocity
        self.health = health
        self.size = size

    def take_damage(self, amount):
        ...

    def update(self, dt):
        ...
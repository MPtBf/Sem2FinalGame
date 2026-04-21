import pygame as pg
from .entity import Entity

class Drone(Entity):
    def __init__(
            self,
            pos: pg.Vector2,
            velocity: pg.Vector2,
            health: float,
            size: tuple,
        ):
        super().__init__(pos, velocity, health, size)
        self.inventory = {}

    def shoot(self):
        ...

    def mine(self):
        ...

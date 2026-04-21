import pygame as pg
from src.models.drone import Drone
from src.models.drill import Drill
from src.models.enemy import Enemy
from src.models.map import Map
from .config import *

class World:
    def __init__(self):
        self.player = Drone(
            pg.Vector2(0,0), pg.Vector2(0,0), 
            100, DRONE_SIZE)
        self.drill = Drill(
            pg.Vector2(0,0), pg.Vector2(0,0), 
            1_000, DRILL_SIZE)
        self.enemies = []
        self.bullets = []
        self.map = Map()
        
    def update(self, dt):
        self.player.update(dt)
        self.drill.update(dt)
        for enemy in self.enemies:
            enemy.update(dt, self.player, self.drill, self.grid)

        self._resolve_collisions()
        self._manage_entities()

    def _resolve_collisions(self):
        ...
        
    def _manage_entities(self):
        ...
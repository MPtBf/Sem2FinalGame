import pygame as pg
from src.models.drone import Drone
from src.models.drill import Drill
from src.models.enemy import Enemy
from src.models.map import Map
from .config import *

class World:
    def __init__(self):
        self.player = Drone(
            pg.Vector2(0,0), 100
        )
        self.drill = Drill(
            pg.Vector2(0,0), 1_000
        )
        self.enemies = []
        self.projectiles = []
        self.map = Map()
        
    def update(self, dt, intents):
        self.player.handle_intents(intents)
        self.player.update(dt)
        self.drill.update(dt)
        for enemy in self.enemies:
            enemy.update(dt, self.player, self.drill, self.grid)

        self._resolve_collisions()
        self._manage_entities()

    def get_all_objects(self):
        return self.enemies + self.projectiles + self.map.get_tiles_list() + \
            [self.player, self.drill]

    def _resolve_collisions(self):
        ...
        
    def _manage_entities(self):
        ...
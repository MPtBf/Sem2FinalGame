import pygame as pg

from src.models.drone import Drone
from src.models.map import Map, Tile
from .game_object import LivingEntity, ObjectType
from src.core.config import DRILL_SIZE, DRILL_SPEED, GroundMaterial

class Drill(LivingEntity):
    def __init__(self, pos: pg.Vector2, health):
        super().__init__(pos, pg.Vector2(*DRILL_SIZE), ObjectType.DRILL, health)
        self.storage = {}

    def update_velocity(self, dt, drone):
        if self._is_saddled_by_drone(drone):
            self.velocity.y = -DRILL_SPEED
        else:
            self.velocity.y = 0

    def _is_saddled_by_drone(self, drone: Drone):
        return self.rect.colliderect(drone.rect)

    def mine(self, map_obj):
        # find tiles we are colliding with
        tiles = map_obj.get_tiles_list()
        collided_with_tiles = [o for o in tiles if o.rect.colliderect(self.rect)]
        
        for wall in collided_with_tiles:
            if wall.ground_material == GroundMaterial.AIR:
                continue

            map_obj.mine(wall)
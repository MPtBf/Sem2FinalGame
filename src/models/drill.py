import pygame as pg

from src.core import event_bus
from src.models.drone import Drone
from src.models.map import Map, Tile
from .game_object import LivingEntity, ObjectType
from src.settings.base import GroundMaterial, EventType
from src.settings.balance import DRILL_SPEED, DRILL_HEALTH
from src.settings.visual import DRILL_SIZE

class Drill(LivingEntity):
    def __init__(self, pos: pg.Vector2, event_bus):
        super().__init__(pos, pg.Vector2(*DRILL_SIZE), ObjectType.DRILL, DRILL_HEALTH)
        self.storage = {}
        self.event_bus = event_bus

    def update_logic(self, dt, world, intents=None):
        super().update_logic(dt, world, intents)
        
        if self._is_saddled_by_drone(world.drone):
            self.velocity.y = -DRILL_SPEED
        else:
            self.velocity.y = 0

    def after_move(self, axis, world):
        # Drill mines after moving along each axis (made for future: diagonal movement)
        self.mine(world.map)

    def _is_saddled_by_drone(self, drone: Drone):
        return self.rect.colliderect(drone.rect) and drone.is_alive

    def mine(self, map_obj: Map):
        # find tiles we are colliding with using optimized grid lookup
        collided_with_tiles = map_obj.get_tiles_in_rect(self.rect)
        
        for wall in collided_with_tiles:
            if wall.ground_material == GroundMaterial.AIR:
                continue

            map_obj.mine(wall, self.velocity)

    
    def die(self):
        self.is_visible = False
        self.velocity *= 0
        self.event_bus.emit(EventType.GAME_OVER)

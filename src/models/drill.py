import pygame as pg

from src.core import event_bus
from src.models.drone import Drone
from src.models.map import Map, Tile
from .game_object import LivingEntity, ObjectType
from src.settings.base import GroundMaterial, EventType
from src.settings.balance import DRILL_ACCELERATION, DRILL_DECELERATION, DRILL_MAX_SPEED, DRILL_HEALTH, DRONE_ACCELERATION
from src.settings.visual import DRILL_SIZE

class Drill(LivingEntity):
    def __init__(self, pos: pg.Vector2, event_bus):
        super().__init__(pos, pg.Vector2(*DRILL_SIZE), ObjectType.DRILL, DRILL_HEALTH)
        self.storage = {}
        self.event_bus = event_bus
        self.acceleration = pg.Vector2(0, 0)

    def update_logic(self, dt, world, intents=None):
        super().update_logic(dt, world, intents)

        # determine desired acceleration
        if self._is_saddled_by_drone(world.drone):
            self.acceleration = pg.Vector2(self.acceleration.x, -DRILL_ACCELERATION)
        else:
            # apply deceleration
            if self.velocity.length() - self.acceleration.length() > 0:
                deceleration = -self.velocity.normalize() * DRILL_DECELERATION
                self.acceleration = deceleration
            else:
                self.acceleration *= 0
                self.velocity *= 0

        # update velocity with acceleration
        self.velocity += self.acceleration
        if self.velocity.length() > DRILL_MAX_SPEED:
            self.velocity.normalize_ip()
            self.velocity *= DRILL_MAX_SPEED

    def after_move(self, axis, world):
        # Drill mines after moving along each axis (made for future: diagonal movement)
        self.mine(world.map)

    def _is_saddled_by_drone(self, drone: Drone):
        return self.rect.colliderect(drone.rect) and drone.is_alive

    def mine(self, map_obj: Map):
        # find tiles we are colliding with using optimized grid lookup
        collided_with_tiles = map_obj.get_tiles_in_rect(self.rect)
        
        for wall in collided_with_tiles:
            map_obj.mine(wall.tile_pos, self.velocity)

    
    def die(self):
        self.is_visible = False
        self.velocity *= 0
        self.event_bus.emit(EventType.GAME_OVER)

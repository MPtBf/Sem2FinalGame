import pygame as pg

from src.core import event_bus
from src.models.drone import Drone
from src.models.map import Map, Tile
from .game_object import LivingEntity, ObjectType
from src.settings.base import GroundMaterial, EventType, Intent
from src.settings.balance import DRILL_ACCELERATION, DRILL_DECELERATION, DRILL_MAX_SPEED, DRILL_HEALTH, DRILL_SIZE, DRONE_ACCELERATION, ENTITY_TO_MINE_EFFICIENCY

class Drill(LivingEntity):
    def __init__(self, pos: pg.Vector2, event_bus, debug):
        super().__init__(pos, pg.Vector2(*DRILL_SIZE), ObjectType.DRILL, DRILL_HEALTH)
        self.storage = {}
        self.event_bus = event_bus
        self._is_toggled = False  # toggle movement by player input
        self.debug = debug
        self._is_holding_toggle = False

    def update_logic(self, dt, world, intents=None):
        super().update_logic(dt, world, intents)

        # handle toggle intent with hold detection
        if intents and Intent.TOGGLE_DRILL in intents.keys():
            if not self._is_holding_toggle:
                self._is_toggled = not self._is_toggled
                self._is_holding_toggle = True
        else:
            # reset holding flag when key not pressed
            self._is_holding_toggle = False

        # determine desired acceleration only when toggled and saddled by drone
        if self._is_saddled_by_drone(world.drone) and self._is_toggled:
            self._acceleration = pg.Vector2(self.acceleration.x, -DRILL_ACCELERATION)
        else:
            # apply deceleration
            if self._velocity.length() - self.acceleration.length() > 0:
                deceleration = -self._velocity.normalize() * DRILL_DECELERATION
                self._acceleration = deceleration
            else:
                self._acceleration *= 0
                self._velocity *= 0

        # update velocity with acceleration
        self._velocity += self.acceleration
        if self._velocity.length() > DRILL_MAX_SPEED:
            self._velocity.normalize_ip()
            self._velocity *= DRILL_MAX_SPEED

    def after_move(self, axis, world):
        # Drill mines after moving along each axis (made for future: diagonal movement)
        self.mine(world.map, world.dt)

    def _is_saddled_by_drone(self, drone: Drone):
        return self.rect.colliderect(drone.rect) and drone.is_alive

    def mine(self, map_obj: Map, dt):
        # find tiles we are colliding with using optimized grid lookup
        collided_with_tiles = map_obj.get_tiles_in_rect(self.rect)
        
        for wall in collided_with_tiles:
            map_obj.mine(wall.tile_pos, self._velocity, dt, self)

    def heal(self, abount: int):
        self.health += abount
    
    def die(self):
        self.is_visible = False
        self._velocity *= 0
        self.event_bus.emit(EventType.GAME_OVER)

import pygame as pg

from src.models.map import Tile
from .game_object import LivingEntity, ObjectType
from src.settings.base import INTENT
from src.settings.balance import DRONE_MAX_SPEED, DRONE_ACCELERATION, DRONE_DECELERATION, DRONE_HEALTH
from src.settings.visual import DRONE_SIZE
from src.core.event_bus import EventType


class Drone(LivingEntity):
    def __init__(self, pos: pg.Vector2):
        super().__init__(pos, pg.Vector2(*DRONE_SIZE), ObjectType.DRONE, DRONE_HEALTH)
        self.inventory = {}
        self.acceleration = pg.Vector2(0, 0)
        self.event_bus = None  # added from WorldHandler separately

        self.move_x_map = {INTENT.MOVE_LEFT: -1, INTENT.MOVE_RIGHT: 1}
        self.move_y_map = {INTENT.MOVE_UP: -1, INTENT.MOVE_DOWN: 1}
        self.action_map = {
            INTENT.SHOOT: self.shoot,
            INTENT.MINE: self.mine,
        }

    def update_logic(self, dt, world, intents=None):
        super().update_logic(dt, world, intents)
        if intents is None:
            intents = {}
        self.handle_intents(intents, dt)

    def handle_intents(self, intents: dict, dt):
        # getting desired acceleration frm intents
        desired_acc = pg.Vector2(0, 0)
        desired_acc.x = sum(self.move_x_map.get(intent, 0) for intent in intents)
        desired_acc.y = sum(self.move_y_map.get(intent, 0) for intent in intents)

        # calculatng accceleration
        if desired_acc.length() > 0:
            desired_acc.normalize_ip()
            desired_acc *= DRONE_ACCELERATION
            self.acceleration = desired_acc
        # calculatng deceleration
        else:
            if self.velocity.length() - self.acceleration.length() > 0:
                self.acceleration = -self.velocity.normalize() * DRONE_DECELERATION
            else:
                self.acceleration *= 0
                self.velocity *= 0

        # updating velocity
        self.velocity += self.acceleration
        # preventing infinite speed by nulling acceleration
        if self.velocity.length() > DRONE_MAX_SPEED:
            self.velocity.normalize_ip()
            self.velocity *= DRONE_MAX_SPEED

        # other intents like shoot and mine
        for intent, data in intents.items():
            if intent in self.action_map:
                self.action_map[intent](data)

    def shoot(self, direction: pg.Vector2):
        spawn_pos = self.pos + self.size / 2
        self.event_bus.emit(EventType.PROJECTILE_SPAWN, pos=spawn_pos, direction=direction, shooter_velocity=pg.Vector2(self.velocity))

    def mine(self, tiles: list[Tile]):
        ...

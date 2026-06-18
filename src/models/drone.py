import pygame as pg

from src.models.map import Map, Tile
from .game_object import LivingEntity, ObjectType
from src.settings.base import MATERIAL_TO_ITEM_MAP, TILE_SIZE, Intent, MineIntent, ShootIntent
from src.settings.balance import DRONE_MAX_SPEED, DRONE_ACCELERATION, DRONE_DECELERATION, DRONE_HEALTH, MINE_REACH_DIST
from src.settings.visual import DRONE_SIZE
from src.core.event_bus import EventType


class Drone(LivingEntity):
    def __init__(self, pos: pg.Vector2, debug):
        super().__init__(pos, pg.Vector2(*DRONE_SIZE), ObjectType.DRONE, DRONE_HEALTH)
        self.inventory = {item: 0 for material, item in MATERIAL_TO_ITEM_MAP.items()}
        self.acceleration = pg.Vector2(0, 0)
        self.event_bus = None  # added from WorldHandler separately
        self.debug = debug

        self.move_x_map = {Intent.MOVE_LEFT: -1, Intent.MOVE_RIGHT: 1}
        self.move_y_map = {Intent.MOVE_UP: -1, Intent.MOVE_DOWN: 1}
        self.action_map = {
            Intent.SHOOT: self.shoot,
            Intent.MINE: self.mine,
        }

    def update_logic(self, dt, world, intents=None):
        if not self.is_alive():
            return

        super().update_logic(dt, world, intents)
        if intents is None:
            intents = {}
        self.handle_intents(intents, world)

    def handle_intents(self, intents: dict, world):
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
        for intent, payload in intents.items():
            if intent in self.action_map:
                self.action_map[intent](payload, world.map)

    def shoot(self, payload: ShootIntent, *args):
        spawn_pos = self.pos + self.size / 2
        self.event_bus.emit(EventType.PLAYER_SHOOT, pos=spawn_pos, 
            direction=payload.direction, shooter_velocity=pg.Vector2(self.velocity))

    def mine(self, payload: MineIntent, map: Map = None):
        direction = payload.mouse_pos - (self.pos + self.size / 2)
        drone_center_pos = self.pos + self.size / 2
        direction.scale_to_length(MINE_REACH_DIST)
        mine_world_pos = drone_center_pos + direction
        map.mine(mine_world_pos // TILE_SIZE, direction, drone=self)
        self.debug.set('inventiry', self.inventory)

    def die(self):
        self.is_visible = False
        self.velocity *= 0
        self.event_bus.emit(EventType.PLAYER_DEATH)

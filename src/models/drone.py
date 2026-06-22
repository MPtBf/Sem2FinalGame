import pygame as pg

from src.models.map import Map, Tile
from .game_object import LivingEntity, ObjectType
from src.settings.base import MATERIAL_TO_ITEM_MAP, TILE_SIZE, Intent, ItemType, MineIntent, ShootIntent
from src.settings.balance import (
    DRONE_MAX_SPEED, DRONE_ACCELERATION, DRONE_DECELERATION, DRONE_HEALTH,
    DRONE_SIZE, MINE_REACH_DIST, DRONE_SHOOT_COOLDOWN
)
from src.core.event_bus import EventBus, EventType


class Drone(LivingEntity):
    """дрон. Игрок"""
    def __init__(self, pos: pg.Vector2, debug):
        super().__init__(pos, pg.Vector2(*DRONE_SIZE), ObjectType.DRONE, DRONE_HEALTH)
        self.inventory = {item: 0 for item in ItemType}
        self.event_bus: EventBus = None  # added from WorldHandler separately
        self.debug = debug
        
        self.is_holding_heal = False
        self.shoot_cooldown_timer = 0.0

        self.move_x_map = {Intent.MOVE_LEFT: -1, Intent.MOVE_RIGHT: 1}
        self.move_y_map = {Intent.MOVE_UP: -1, Intent.MOVE_DOWN: 1}
        self.action_map = {
            Intent.SHOOT: self.shoot,
            Intent.MINE: self.mine,
            Intent.HEAL_DRILL: self.heal_drill,
        }

    def update_logic(self, dt: float, world, intents=None) -> None:
        """обновление логики игрока - обработка интентов, обновление физики"""
        if not self.is_alive():
            return

        super().update_logic(dt, world, intents)
        if self.shoot_cooldown_timer > 0:
            self.shoot_cooldown_timer -= dt

        if intents is None:
            intents = {}
        self._handle_intents(intents, world)
        self._update_physics()
        
        self.debug.set('player pos', (*self.pos,))

    def _handle_intents(self, intents: dict, world) -> None:
        """обработка интентов. Обновляет скорость и действия игрока."""
        # getting desired acceleration frm intents
        desired_acc = pg.Vector2(0, 0)
        desired_acc.x = sum(self.move_x_map.get(intent, 0) for intent in intents)
        desired_acc.y = sum(self.move_y_map.get(intent, 0) for intent in intents)

        # calculatng accceleration
        if desired_acc.length() > 0:
            desired_acc.normalize_ip()
            desired_acc *= DRONE_ACCELERATION
            self._acceleration = desired_acc
        # calculatng deceleration
        else:
            if self._velocity.length() - self._acceleration.length() > 0:
                self._acceleration = -self._velocity.normalize() * DRONE_DECELERATION
            else:
                self._acceleration *= 0
                self._velocity *= 0

        # other intents like shoot and mine
        for intent, payload in intents.items():
            if intent in self.action_map:
                self.action_map[intent](payload, world.map, world.dt)

        if Intent.HEAL_DRILL not in intents.keys():
            self.is_holding_heal = False

    def _update_physics(self) -> None:
        """обновление физики игрока - применение скорости, обреание до максимума"""
        # updating velocity
        self._velocity += self._acceleration
        # preventing infinite speed by nulling acceleration
        if self._velocity.length() > DRONE_MAX_SPEED:
            self._velocity.normalize_ip()
            self._velocity *= DRONE_MAX_SPEED

    def shoot(self, payload: ShootIntent, *args) -> None:
        """стрельба. Отправляет событие PLAYER_SHOOT, если не в cooldown"""
        if self.shoot_cooldown_timer > 0:
            return

        spawn_pos = self.pos + self.size / 2
        self.event_bus.emit(EventType.PLAYER_SHOOT, pos=spawn_pos,
            direction=payload.direction, shooter_velocity=pg.Vector2(self._velocity))
        self.shoot_cooldown_timer = DRONE_SHOOT_COOLDOWN

    def mine(self, payload: MineIntent, map: Map, dt: float) -> None:
        """копание тайлов на карте. Вызывает mine у Map, если копание возможно"""
        direction = payload.mouse_pos - (self.pos + self.size / 2)
        drone_center_pos = self.pos + self.size / 2
        direction.scale_to_length(MINE_REACH_DIST)
        mine_world_pos = drone_center_pos + direction
        map.mine(mine_world_pos // TILE_SIZE, direction, dt, entity=self)
        self.debug.set('inventiry', self.inventory)

    def die(self) -> None:
        """смерть. Отправляет событие PLAYER_DEATH"""
        self._velocity *= 0
        self.event_bus.emit(EventType.PLAYER_DEATH)

    def heal_drill(self, *args) -> None:
        """лечение бура засчёт меди"""
        if self.is_holding_heal:
            return
        self.event_bus.emit(EventType.HEAL_DRILL)
        self.is_holding_heal = True

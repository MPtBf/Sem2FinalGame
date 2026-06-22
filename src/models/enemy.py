
import pygame as pg

from src.core.event_bus import EventBus
from .game_object import GameObject, LivingEntity
from src.settings.balance import ENEMY_HEALTH, ENEMY_CONTACT_DAMAGE, ENEMY_DAMAGE_COOLDOWN_SEC, ENEMY_DECELERATION, ENEMY_SIZE, KNOCKBACK_FORCE, ENEMY_MAX_SPEED, ENEMY_ACCELERATION, ENEMY_NOTICING_RADIUS
from src.settings.base import FMSState, PlayerState, EventType, ObjectType, GroundMaterial, TILE_SIZE
from src.utils.astar import find_path


class Enemy(LivingEntity):
    def __init__(self, pos: pg.Vector2, event_bus: EventBus):
        super().__init__(
            pos,
            pg.Vector2(*ENEMY_SIZE),
            ObjectType.ENEMY,
            ENEMY_HEALTH
        )
        self._damage_cooldown = 0.0
        self._acceleration = pg.Vector2(0, 0)
        self.event_bus = event_bus

        self.state = FMSState.IDLE
        self.target_pos: pg.Vector2 = None
        self._path = []
        self._path_timer = 0.0
        self._path_update_interval = 0.3

    def update_logic(self, dt, world, intents=None) -> None:
        """Обновление логики врага - обработка интентов, обновление физики"""

        super().update_logic(dt, world, intents)
        if self._damage_cooldown > 0:
            self._damage_cooldown -= dt

        self._update_intents(dt, world)

    def _find_target(self, world) -> None:
        """Находит цель - игрока или бур, если они живы и в зоне видимости. Обновляет состояние и цель"""
        # movement towards nearest of drone (if player alive) or drill
        vec_to_drone = world.drone.pos + world.drone.size/2 - self.pos - self.size/2
        vec_to_drill = world.drill.pos + world.drill.size/2 - self.pos - self.size/2
        dist_to_drone = vec_to_drone.length()
        dist_to_drill = vec_to_drill.length()

        # gather candidate targets (distance, vector) where distance > 0
        candidates = []
        if world.player_state == PlayerState.ALIVE:
            candidates.append((dist_to_drone, vec_to_drone))
        candidates.append((dist_to_drill, vec_to_drill))

        # choose nearest candidate if exist
        if candidates:
            target_dist, target_vec = min(candidates, key=lambda x: x[0])
        else:
            target_dist = float('inf')
            target_vec = pg.Vector2(0, 0)

        if 0 < target_dist <= ENEMY_NOTICING_RADIUS:
            self.target_pos = self.pos + target_vec
            self.state = FMSState.CHASING
        else:
            self.target_pos = None
            self.state = FMSState.IDLE

    def _update_intents(self, dt, world) -> None:
        """Обработка интентов. Обновляет скорость и действия"""
        # select target
        self._find_target(world)

        # do action
        if self.state == FMSState.IDLE:
            self._path = []
            self._walk_around()
        elif self.state == FMSState.CHASING:
            self._chase_target(dt, world)

        self._update_physics()

    def _walk_around(self) -> None:
        """состояние IDLE"""
        ...  # walk around randomly (in the future)

        # calculatng deceleration
        if self._velocity.length() - self._acceleration.length() > 0:
            self._acceleration = -self._velocity.normalize() * ENEMY_DECELERATION
        else:
            self._acceleration *= 0
            self._velocity *= 0

    def _chase_target(self, dt, world) -> None:
        """состояние CHASING, движение к цели по A*"""
        if not self.target_pos:
            self._acceleration *= 0
            return

        # Находим координаты плиток для врага и цели
        enemy_tile = (
            int((self.pos.x + self.size.x / 2) // TILE_SIZE),
            int((self.pos.y + self.size.y / 2) // TILE_SIZE)
        )
        target_tile = (
            int(self.target_pos.x // TILE_SIZE),
            int(self.target_pos.y // TILE_SIZE)
        )

        # Периодически обновляем путь
        self._path_timer += dt
        if not self._path or self._path_timer >= self._path_update_interval:
            self._path_timer = 0.0
            self._path = find_path(world.map.tiles, enemy_tile, target_tile)
            if self._path is None:
                self._path = []

        # Удаляем из пути плитки, которые враг уже прошел
        while self._path and enemy_tile == self._path[0]:
            self._path.pop(0)

        # Выбираем целевую точку для движения
        if self._path:
            next_tile = self._path[0]
            target_world_pos = pg.Vector2(
                next_tile[0] * TILE_SIZE + TILE_SIZE / 2,
                next_tile[1] * TILE_SIZE + TILE_SIZE / 2
            )
        else:
            target_world_pos = self.target_pos

        target_vec = target_world_pos - (self.pos + self.size / 2)

        # calculate acceleration
        if target_vec.length() > 0:
            direction = target_vec.normalize()
            self._acceleration = direction * ENEMY_ACCELERATION
        # calculatng deceleration
        else:
            if self._velocity.length() - self._acceleration.length() > 0:
                self._acceleration = -self._velocity.normalize() * ENEMY_DECELERATION
            else:
                self._acceleration *= 0
                self._velocity *= 0

    def _update_physics(self) -> None:
        """Обновляет физику врага"""
        self._velocity += self._acceleration

        # limit speed to max speed
        if self._velocity.length() > ENEMY_MAX_SPEED:
            self._velocity.scale_to_length(ENEMY_MAX_SPEED)

    def try_damage(self, target, knockback_direction: pg.Vector2 = None) -> bool:
        """попытка ударить target сущность. ызывает target.take_damage если кулдакн позволяет"""
        if self._damage_cooldown <= 0:
            target.take_damage(ENEMY_CONTACT_DAMAGE, knockback_direction)
            self._damage_cooldown = ENEMY_DAMAGE_COOLDOWN_SEC
            return True
        return False

    def die(self) -> None:
        """смерть врага. Вызывает событие ENEMY_DEATH"""
        self.event_bus.emit(EventType.ENEMY_DEATH, enemy=self)

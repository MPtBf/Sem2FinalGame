

from enum import Enum, auto
import random
from src.settings.balance import COPPER_NOISE_SIZE, COPPER_NOISE_THRESHOLD, ENTITY_TO_MINE_EFFICIENCY, HARD_STONE_NOISE_SIZE, HARD_STONE_NOISE_THRESHOLD, MINE_TIME_SPREAD
from src.settings.base import (
    MATERIAL_TO_ITEM_MAP, SPAWN_SPACE_OFFSET_TILES, SPAWN_SPACE_RADIUS_TILES, TILE_SIZE, GroundMaterial
)
from src.settings.cave_config import SPAWN_CHANCE_BASE, MIN_TILES_BETWEEN
from src.core.event_bus import EventBus, EventType
from src.models.game_object import GameObject, LivingEntity, ObjectType
import pygame as pg
from src.utils.shortcuts import TC
from src.models.cave import Cave
from src.utils.debug_collector import DebugCollector
from src.settings.balance import MATERIAL_TO_MINE_TIME
from src.utils.perlin_noise import PerlinNoise


class Tile(GameObject):
    """тайл карты. Материал, прочность"""
    def __init__(self, pos: pg.Vector2, ground_material: GroundMaterial):
        super().__init__(pos, pg.Vector2(TILE_SIZE, TILE_SIZE), ObjectType.GROUND)
        self.ground_material = ground_material
        # time to mine the tile
        spread = random.uniform(-MINE_TIME_SPREAD/2, MINE_TIME_SPREAD/2)
        self.durability = MATERIAL_TO_MINE_TIME.get(ground_material, 100) + spread

    def destroy(self):
        """разрушает тайл. Изменяет материал на AIR"""
        self.ground_material = GroundMaterial.AIR

    @property
    def tile_pos(self):
        return self.pos // TILE_SIZE
    


class Map:
    """карта. Массив тайлов, обработка добычи, генерации карты"""
    def __init__(self, event_bus: EventBus, debug: DebugCollector) -> None:
        # no xy pair - unexplored area
        self.event_bus = event_bus
        self.debug = debug
        self._tiles: dict[tuple[int, int], Tile] = {}
        self.tiles_mined_since_last_cave = 0

        self.seed = random.random()
        self._vn = PerlinNoise(seed=self.seed)

        self._init_start_zone()

    def _get_generated_copper(self, tile_pos) -> bool:
        """проверяет, сгенерировать ли тайл сopper"""
        noise_pos = tile_pos[0] / COPPER_NOISE_SIZE, tile_pos[1] / COPPER_NOISE_SIZE
        val = self._vn.noise(*noise_pos)
        return val > COPPER_NOISE_THRESHOLD

    def _get_generated_hard_stone(self, tile_pos) -> bool:
        """проверяет, сгенерировать ли тайл hard stone"""
        noise_pos = tile_pos[0] / HARD_STONE_NOISE_SIZE, tile_pos[1] / HARD_STONE_NOISE_SIZE
        val = self._vn.noise(*noise_pos)
        return val > HARD_STONE_NOISE_THRESHOLD

    def _init_start_zone(self) -> None:
        """инициализирует начальный зону спавна. Генерирует круг пустых тайлов с тонким стенами"""

        rad = SPAWN_SPACE_RADIUS_TILES
        off_x, off_y = SPAWN_SPACE_OFFSET_TILES
        safe_air_radius = rad + 2
        # generate spawn zone: circle of air with a thin stone wall
        for x in range(int(-safe_air_radius + off_x), int(safe_air_radius + off_x)):
            for y in range(int(-safe_air_radius + off_y), int(safe_air_radius + off_y)):
                if ((x - off_x)**2 + (y - off_y)**2)**0.5 <= rad:
                    self._tiles[(x,y)] = Tile(
                        pg.Vector2(*TC(x, y)), GroundMaterial.AIR)
                elif ((x - off_x)**2 + (y - off_y)**2)**0.5 <= (rad + 1):
                    material = self._get_generated_tile_material((x,y))
                    self._tiles[(x,y)] = Tile(
                        pg.Vector2(*TC(x, y)), material)

    def _get_generated_tile_material(self, tile_pos) -> GroundMaterial:
        """решает, сгенерировать ли тайл сopper, hard stone или stone в заданной точке"""
        if self._get_generated_copper(tile_pos):
            return GroundMaterial.COPPER
        if self._get_generated_hard_stone(tile_pos):
            return GroundMaterial.HARD_STONE
        return GroundMaterial.STONE

    def get_tile_at(self, tile_pos) -> Tile:
        """возвращает тайл в заданной точке. Если тайл не существует, возвращает None"""
        return self._tiles.get((*tile_pos,))
        
    def get_tiles_list(self) -> list[Tile]:
        """возвращает список всех тайлов на карте в виде списка"""
        tiles_list = list(self._tiles.values())
        return [v for v in tiles_list if v is not None]

    @property
    def tiles(self):
        return self._tiles

    def get_tiles_in_rect(self, rect: pg.Rect) -> list[Tile]:
        """возвращает список всех тайлов в заданной прямоугольнике"""
        # rect boundaries to tile coordinats
        start_x = rect.left // TILE_SIZE
        end_x = rect.right // TILE_SIZE
        start_y = rect.top // TILE_SIZE
        end_y = rect.bottom // TILE_SIZE

        tiles = []
        for x in range(int(start_x), int(end_x) + 1):
            for y in range(int(start_y), int(end_y) + 1):
                tile = self._tiles.get((x, y))
                if tile:
                    tiles.append(tile)
        return tiles

    def mine(self, tile_pos_vec: pg.Vector2, direction: pg.Vector2, dt: float, entity: LivingEntity) -> None:
        """добыча тайла в заданной точке. Прогресс поломки, генерация новой области, генерация пещер"""
        tile_pos = (*tile_pos_vec,)

        # if trying to mine unexplored area, explore first
        tile = self._tiles.get(tile_pos)
        if tile is None:
            self.generate_tile_at(tile_pos)
            tile = self._tiles.get(tile_pos)

        # if tile already air, nothing to mine
        if tile.ground_material == GroundMaterial.AIR:
            return

        # reduce durability based on efficiency and dt
        efficiency = ENTITY_TO_MINE_EFFICIENCY[entity.object_type]
        if dt > 0:
            tile.durability -= dt * efficiency
            if tile.durability > 0:
                # not yet mined completely
                return
            # durability exhausted, treat as mined
            tile.durability = 0

        if entity.object_type == ObjectType.DRONE:
            self._handle_item_pickup(entity, tile.ground_material)
        tile.destroy()

        self.tiles_mined_since_last_cave += 1

        # spawn caves with pseudo-random
        if self.tiles_mined_since_last_cave >= MIN_TILES_BETWEEN:
            chance = SPAWN_CHANCE_BASE
            if random.random() < chance:
                cave = Cave(self._vn, self, self.event_bus, self.debug)
                success = cave.generate_cave(pg.Vector2(tile_pos), direction)
                self.tiles_mined_since_last_cave = 0
                if success:
                    self.debug.increase('cave spawn general successes:', 1)
                else:
                    self.debug.increase('cave spawn general failures:', 1)

        # generate neighbors for "unexplored" area tiles
        self._generate_neighbours(tile_pos)

    def _handle_item_pickup(self, drone, material: GroundMaterial) -> None:
        """обработка сбора предмета из добытого тайла. Даёт дрону предмет"""
        if material not in MATERIAL_TO_ITEM_MAP.keys():
            return
        item_type = MATERIAL_TO_ITEM_MAP[material]
        drone.inventory[item_type] += 1

    def _generate_neighbours(self, tile_pos: tuple[int,int]) -> None:
        """генерация соседних тайлов вокруг заданной позиции"""
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neigh = (tile_pos[0] + dx, tile_pos[1] + dy)
            if self._tiles.get(neigh) is None:
                self.generate_tile_at(neigh)

    def set_raw(self, tile_pos: tuple[int,int], material: GroundMaterial) -> None:
        """устанавливает тайл в заданной позиции с заданным материалом без генерации соседей"""
        self._tiles[tile_pos] = Tile(pg.Vector2(*TC(tile_pos)), material)

    def generate_tile_at(self, tile_pos: tuple[int,int]) -> None:
        """генерирует тайл в заданной позиции. Решает, какой материал установить"""
        material = self._get_generated_tile_material(tile_pos)
        existing = self._tiles.get(tile_pos)
        if existing:
            if existing.ground_material == material:
                return
            existing.ground_material = material
        else:
            self._tiles[tile_pos] = Tile(pg.Vector2(*TC(tile_pos)), material)
        



from enum import Enum, auto
import random
from src.settings.base import (
    SPAWN_SPACE_OFFSET_TILES, SPAWN_SPACE_RADIUS_TILES, TILE_SIZE, GroundMaterial
)
from src.settings.balance import CAVE_SPAWN_CHANCE_BASE, CAVE_MIN_TILES_BETWEEN
from src.core.event_bus import EventBus, EventType
from src.models.game_object import GameObject, ObjectType
import pygame as pg
from src.utils.shortcuts import TC
from src.models.cave import CaveGenerator


class Tile(GameObject):
    def __init__(self, pos: pg.Vector2, ground_material: GroundMaterial):
        super().__init__(pos, pg.Vector2(TILE_SIZE, TILE_SIZE), ObjectType.GROUND)
        self.ground_material = ground_material

    def destroy(self):
        self.ground_material = GroundMaterial.AIR
    


class Map:
    def __init__(self, event_bus: EventBus) -> None:
        # no xy pair - unexplored area
        self.event_bus = event_bus
        self._tiles: dict[tuple[int, int], Tile] = {}
        self._tiles_mined_since_last_cave = 0

        self._init_start_zone()

    def _init_start_zone(self):
        
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
                    self._tiles[(x,y)] = Tile(
                        pg.Vector2(*TC(x, y)), GroundMaterial.STONE)

        
    def get_tiles_list(self):
        tiles_list = list(self._tiles.values())
        return [v for v in tiles_list if v is not None]

    def get_tiles_in_rect(self, rect: pg.Rect) -> list[Tile]:
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

    def mine(self, tile: Tile, direction: pg.Vector2 = pg.Vector2(0, 0)):
        tile_pos = TC(tile.rect.topleft, revert=True)
        if self._tiles.get(tile_pos) is None:
            return

        # change material to air
        tile.destroy()
        self._tiles_mined_since_last_cave += 1

        # spawn caves with pseudo-random
        if self._tiles_mined_since_last_cave >= CAVE_MIN_TILES_BETWEEN:
            chance = CAVE_SPAWN_CHANCE_BASE
            if random.random() < chance:
                spawn_positions = CaveGenerator.generate_cave(self, tile_pos, direction)
                if spawn_positions:
                    self.event_bus.emit(EventType.ENEMY_SPAWN, positions=spawn_positions)
                self._tiles_mined_since_last_cave = 0

        # generate neighbors for "unexplored" area tiles
        self._generate_neighbours(tile_pos)

    def set_tile_at(self, tile_pos: tuple[int, int], material: GroundMaterial):
        """Sets or updates a tile at specific coordinates."""
        existing = self._tiles.get(tile_pos)
        if existing:
            if existing.ground_material == material:
                return
            existing.ground_material = material
        else:
            self._tiles[tile_pos] = Tile(pg.Vector2(*TC(tile_pos)), material)

        # ensure spawned walls around air
        if material == GroundMaterial.AIR:
            self._generate_neighbours(tile_pos)

    def _generate_neighbours(self, tile_pos):
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neigh = (tile_pos[0] + dx, tile_pos[1] + dy)
            if self._tiles.get(neigh) is None:
                self.generate_tile(neigh)

    def is_air(self, tile_pos: tuple[int, int]) -> bool:
        """Checks if a tile at given position is Air."""
        tile = self._tiles.get(tile_pos)
        return tile and tile.ground_material == GroundMaterial.AIR

                

    def generate_tile(self, tile_pos: tuple[int, int]):
        """some generation logic like different ores and caves"""
        self._tiles[tile_pos] = Tile(pg.Vector2(*TC(tile_pos)), 
                                     GroundMaterial.STONE)
        

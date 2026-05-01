

from enum import Enum, auto
from src.core.config import TILE_SIZE, Z_INDEX, GroundMaterial
from src.models.game_object import GameObject, ObjectType
import pygame as pg


class Tile(GameObject):
    def __init__(self, pos: pg.Vector2, ground_material: GroundMaterial):
        super().__init__(pos, ObjectType.GROUND)
        self.ground_material = ground_material

    def destroy(self):
        ...
    


class Map:
    def __init__(self) -> None:
        # no xy pair - unexplored area
        self._tiles = {}

        self._init_start_zone()

    def _init_start_zone(self, air_radius=7):
        
        safe_air_radius = air_radius + 2
        for x in range(-safe_air_radius, safe_air_radius):
            for y in range(-safe_air_radius, safe_air_radius):
                if (x**2 + y**2)**0.5 <= air_radius:
                    self._tiles[(x,y)] = Tile(
                        (x * TILE_SIZE, y * TILE_SIZE), GroundMaterial.AIR)
                elif (x**2 + y**2)**0.5 <= (air_radius + 1):
                    self._tiles[(x,y)] = Tile(
                        (x * TILE_SIZE, y * TILE_SIZE), GroundMaterial.STONE)

        
    def get_tiles_list(self):
        tiles_list = list(self._tiles.values())
        return [v for v in tiles_list if v is not None]
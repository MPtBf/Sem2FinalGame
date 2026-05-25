

from enum import Enum, auto
from src.core.config import SPAWN_SPACE_OFFSET_TILES, SPAWN_SPACE_RADIUS_TILES, TILE_SIZE, Z_INDEX, GroundMaterial
from src.models.game_object import GameObject, ObjectType
import pygame as pg
from src.utils.shortcuts import TC


class Tile(GameObject):
    def __init__(self, pos: pg.Vector2, ground_material: GroundMaterial):
        super().__init__(pos, pg.Vector2(TILE_SIZE, TILE_SIZE), ObjectType.GROUND)
        self.ground_material = ground_material

    def destroy(self):
        self.ground_material = GroundMaterial.AIR
    


class Map:
    def __init__(self) -> None:
        # no xy pair - unexplored area
        self._tiles: dict[Tile] = {}

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

    def mine(self, tile: Tile):
        tile_pos = TC(tile.rect.topleft, revert=True)
        if self._tiles.get(tile_pos) is None:
            raise Exception(f'trying to mine non-existent tile at pos: {tile_pos}, material: {tile.ground_material}')

        # сhange material to air
        tile.destroy()
        # generate neighbors for "unexplored" area tiles
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neigh = (tile_pos[0] + dx, tile_pos[1] + dy)
            if self._tiles.get(neigh) is None:
                self.generate_tile(neigh)

                

    def generate_tile(self, tile_pos: tuple[int, int]):
        """some generation logic like different ores and caves"""
        self._tiles[tile_pos] = Tile(pg.Vector2(*TC(tile_pos)), 
                                     GroundMaterial.STONE)
        

import random
import math
import pygame as pg
from src.core.event_bus import EventBus
from src.settings.cave_config import ENEMY_SPAWN_PER_TILE, GEN_MIN_TRY_DISTANCE_TILES, GEN_OFFSET_TRIES, GEN_TRY_OFFSET_SPREAD_TILES, GEN_TRY_OFFSET_TILES, MAIN_CAVE_SCALE_RANGE, MAIN_CAVE_THRESHOLD_RANGE, MAX_RECURSON_DEPTH, NOISE_START_SEARCH_TRIES, VEIN_ANGLE_RANGE, VEIN_SCALE_X_RANGE, VEIN_SCALE_Y_RANGE, VEIN_THRESHOLD_RANGE
from src.settings.base import TILE_SIZE, GroundMaterial, EventType

from src.utils.debug_collector import DebugCollector
from src.utils.perlin_noise import PerlinNoise



class Cave:
    def __init__(self, vn: PerlinNoise, map, event_bus: EventBus, debug: DebugCollector) -> None:
        self.vn = vn
        self.offset_tile_pos = pg.Vector2(0, 0)
        self.map = map
        self.event_bus = event_bus
        self.debug = debug

        self.main_cave_scale = random.uniform(*MAIN_CAVE_SCALE_RANGE)
        self.vein_scale_x = random.uniform(*VEIN_SCALE_X_RANGE)
        self.vein_scale_y = random.uniform(*VEIN_SCALE_Y_RANGE)
        self.vein_angle = random.uniform(*VEIN_ANGLE_RANGE)
        self.main_cave_threshold = random.uniform(*MAIN_CAVE_THRESHOLD_RANGE)
        self.vein_threshold = random.uniform(*VEIN_THRESHOLD_RANGE)

    def generate_cave(self, tile_pos: pg.Vector2, direction: pg.Vector2):
        self.debug.increase('cave spawn general attempts:', 1)

        # find a cave start on the noise picture
        local_start_tile_pos = self._find_noise_cave_start()
        if local_start_tile_pos is None:
            return False
        
        random_offset_tiles = pg.Vector2(random.uniform(-GEN_TRY_OFFSET_SPREAD_TILES, GEN_TRY_OFFSET_SPREAD_TILES), 
            random.uniform(-GEN_TRY_OFFSET_SPREAD_TILES, GEN_TRY_OFFSET_SPREAD_TILES))

        # determine a position on a map offsetting further from mined tile and trying to gen
        for distance in range(GEN_MIN_TRY_DISTANCE_TILES, GEN_MIN_TRY_DISTANCE_TILES + GEN_TRY_OFFSET_TILES * GEN_OFFSET_TRIES, GEN_TRY_OFFSET_TILES):
            direction.scale_to_length(distance)
            self.offset_tile_pos = (tile_pos + direction + random_offset_tiles) // 1
            print(f'{tile_pos} (pos) + {direction} (direction) = ')
            print('= offset:', self.offset_tile_pos)

            # generate cave tiles
            air_tiles_set = set()
            edge_tiles_set = set()
            self._generate_cave_tiles_recurs(air_tiles_set, edge_tiles_set, (*local_start_tile_pos,))
            
            self.debug.increase('cave gen attempts:', 1)

            air_tiles_set = set([(*p + self.offset_tile_pos - local_start_tile_pos,) for p in air_tiles_set])
            edge_tiles_set = set([(*p + self.offset_tile_pos - local_start_tile_pos,) for p in edge_tiles_set])

            # determine if a cave is disjoint
            is_disjoint = self._is_cave_tile_disjoint(air_tiles_set)
            if is_disjoint: 
                break
            
            self.debug.increase('cave gen fail: disjoint', 1)

        if not is_disjoint:
            return False

        if not air_tiles_set:
            self.debug.increase('cave gen fail: no tiles', 1)
            return False

        self._spawn_enemies(air_tiles_set)

        self._carve_cave(air_tiles_set, edge_tiles_set)
        
        self.debug.set('last cave spawn pos:', pg.Vector2(list(air_tiles_set)[0])*TILE_SIZE)
        return True

    def _carve_cave(self, air_tiles_set: set, edge_tiles_set: set):
        for air_tile_pos in air_tiles_set:
            self.map.set_raw(air_tile_pos, GroundMaterial.AIR)  

        for edge_tile_pos in edge_tiles_set:
            self.map.generate_tile_at(edge_tile_pos)

    def _spawn_enemies(self, air_tiles: set):
        air_positions = air_tiles
        if not air_positions:
            return []

        # picking positions
        num_enemies = int(len(air_positions) * ENEMY_SPAWN_PER_TILE)
        num_enemies = min(num_enemies, len(air_positions))
        spawn_positions = random.sample(list(air_positions), num_enemies)
        
        # spawning
        for pos in spawn_positions:
            self.event_bus.emit(EventType.ENEMY_SPAWN, tile_pos=pg.Vector2(pos))

    def _is_cave_tile_disjoint(self, tiles: set):
        for tile_pos in tiles:
            if self.map.get_tile_at(tile_pos) is not None:
                return False
        return True

    def _generate_cave_tiles_recurs(self, air_tiles_set: set, edge_tiles_set: set, start_tile_pos: tuple, recursion_depth: int = 0):
        if start_tile_pos in air_tiles_set or start_tile_pos in edge_tiles_set:
            return
        if recursion_depth > MAX_RECURSON_DEPTH:
            self.debug.increase('cave gen recursion limit hit:', 1)
            edge_tiles_set.add(start_tile_pos)
            return
        if not self._is_cave_at_pos(pg.Vector2(start_tile_pos)):
            edge_tiles_set.add(start_tile_pos)
            return

        air_tiles_set.add(start_tile_pos)
        
        # searching 4 neighs
        for x,y in [(start_tile_pos[0] - 1, start_tile_pos[1]), 
            (start_tile_pos[0] + 1, start_tile_pos[1]), 
            (start_tile_pos[0], start_tile_pos[1] - 1), 
            (start_tile_pos[0], start_tile_pos[1] + 1)]:
                self._generate_cave_tiles_recurs(air_tiles_set, edge_tiles_set, (x, y), recursion_depth + 1)

    def _find_noise_cave_start(self):
        for _ in range(NOISE_START_SEARCH_TRIES):
            # sample some random points on self.vn until find cave
            x, y = random.randint(0, 100), random.randint(0, 100)
            is_cave = self._is_cave_at_pos(pg.Vector2(x, y))
            if is_cave:
                return pg.Vector2(x, y)
            self.debug.increase('cave gen noise start find attempts:', 1)

        return None
            
    def _is_cave_at_pos(self, pos: pg.Vector2):
        # main big caves
        val_main = self.vn.noise(*(pos / self.main_cave_scale))
        
        # long veins with rotation
        rad = math.radians(self.vein_angle)
        tx = (pos.x * math.cos(rad) - pos.y * math.sin(rad)) / self.vein_scale_x
        ty = (pos.x * math.sin(rad) + pos.y * math.cos(rad)) / self.vein_scale_y
        val_veins = self.vn.noise(tx, ty)

        if val_main > self.main_cave_threshold or val_veins > self.vein_threshold:
            return True
        return False


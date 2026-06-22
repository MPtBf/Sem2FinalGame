import random
import math
import pygame as pg
from src.core.event_bus import EventBus
from src.settings.cave_config import ENEMY_SPAWN_PER_TILE, GEN_TRY_MIN_DISTANCE_TILES, GEN_OFFSET_TRIES, GEN_SPREAD_TILES, GEN_TRY_OFFSET_INCREASE_TILES, MAIN_CAVE_SCALE_RANGE, MAIN_CAVE_THRESHOLD_RANGE, NOISE_START_SEARCH_TRIES, VEIN_ANGLE_RANGE, VEIN_SCALE_X_RANGE, VEIN_SCALE_Y_RANGE, VEIN_THRESHOLD_RANGE
from src.settings.base import TILE_SIZE, GroundMaterial, EventType

from src.utils.debug_collector import DebugCollector
from src.utils.perlin_noise import PerlinNoise



class Cave:
    """класс пещеры, генерирует пещеру на основе карты шума"""
    def __init__(self, vn: PerlinNoise, map, event_bus: EventBus, debug: DebugCollector) -> None:
        self.vn = vn
        self.map = map
        self.event_bus = event_bus
        self.debug = debug

        self.main_cave_scale = random.uniform(*MAIN_CAVE_SCALE_RANGE)
        self.vein_scale_x = random.uniform(*VEIN_SCALE_X_RANGE)
        self.vein_scale_y = random.uniform(*VEIN_SCALE_Y_RANGE)
        self.vein_angle = random.uniform(*VEIN_ANGLE_RANGE)
        self.main_cave_threshold = random.uniform(*MAIN_CAVE_THRESHOLD_RANGE)
        self.vein_threshold = random.uniform(*VEIN_THRESHOLD_RANGE)

        vein_rad = math.radians(self.vein_angle)
        self.sin_vein = math.sin(vein_rad)
        self.cos_vein = math.cos(vein_rad)

    def generate_cave(self, tile_pos: pg.Vector2, direction: pg.Vector2) -> bool:
        """генерация пещеры в указанном направлении, начиная с указанной клетки
        returns: True, если пещера была сгенерирована, False при неудаче"""
        self.debug.increase('cave spawn general attempts:', 1)

        # find a cave start on the noise picture
        local_start_tile_pos = self._find_noise_cave_start()
        if local_start_tile_pos is None:
            return False
        
        random_offset_tiles = pg.Vector2(random.uniform(-GEN_SPREAD_TILES, GEN_SPREAD_TILES), 
            random.uniform(-GEN_SPREAD_TILES, GEN_SPREAD_TILES))

        # generate cave tiles once before trying offsets
        base_air_tile_set = set()
        base_edge_tile_set = set()
        self._generate_cave_tiles(base_air_tile_set, base_edge_tile_set, (*local_start_tile_pos,))

        for distance in range(GEN_TRY_MIN_DISTANCE_TILES, GEN_TRY_MIN_DISTANCE_TILES + GEN_TRY_OFFSET_INCREASE_TILES * GEN_OFFSET_TRIES, GEN_TRY_OFFSET_INCREASE_TILES):
            if direction.length() == 0:
                direction = pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            
            direction.scale_to_length(distance)
            offset_tile_pos = (tile_pos + direction + random_offset_tiles) // 1

            # apply current offset to base tiles
            air_tile_set = set([(*p + offset_tile_pos - local_start_tile_pos,) for p in base_air_tile_set])
            edge_tile_set = set([(*p + offset_tile_pos - local_start_tile_pos,) for p in base_edge_tile_set])

            # determine if a cave is disjoint
            is_disjoint = self._is_cave_tile_disjoint(air_tile_set)
            if is_disjoint:
                break

            self.debug.increase('cave gen retried: disjoint', 1)

        if not is_disjoint:
            return False

        if not air_tile_set:
            self.debug.increase('cave gen fail: no tiles', 1)
            return False

        self._spawn_enemies(air_tile_set)

        self._carve_cave(air_tile_set, edge_tile_set)
        
        return True

    def _carve_cave(self, air_tiles_set: set, edge_tiles_set: set) -> None:
        """занесение тайлов пещеры на карту"""
        for air_tile_pos in air_tiles_set:
            self.map.set_raw(air_tile_pos, GroundMaterial.AIR)  

        for edge_tile_pos in edge_tiles_set:
            self.map.generate_tile_at(edge_tile_pos)

    def _spawn_enemies(self, air_tiles: set) -> None:
        """случайная генерация врагов на месте пустых тайлов пещеры"""
        air_positions = air_tiles
        if not air_positions:
            return

        # picking positions
        num_enemies = int(len(air_positions) * ENEMY_SPAWN_PER_TILE)
        num_enemies = min(num_enemies, len(air_positions))
        spawn_positions = random.sample(list(air_positions), num_enemies)
        
        # spawning
        for pos in spawn_positions:
            self.event_bus.emit(EventType.ENEMY_SPAWN, tile_pos=pg.Vector2(pos))

    def _is_cave_tile_disjoint(self, tiles: set) -> bool:
        """проверка, не пересекается ли пещера с уже открытыми областями на карте"""
        if not tiles:
            return True
        for tile_pos in tiles:
            if self.map.get_tile_at(tile_pos) is not None:
                return False
        return True

    def _generate_cave_tiles(self, air_tiles_set: set, edge_tiles_set: set, start_tile_pos: tuple) -> None:
        """итеративное нахождение всех тайлов пещеры на карте шума, начиная с указанной клетки
        returns: None"""
        queue = [start_tile_pos]
        
        while queue:
            current = queue.pop(0)
            
            if current in air_tiles_set or current in edge_tiles_set:
                continue
                
            if not self._is_cave_at_pos(pg.Vector2(current)):
                edge_tiles_set.add(current)
                continue
                
            air_tiles_set.add(current)
            
            # searching 4 neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor not in air_tiles_set and neighbor not in edge_tiles_set:
                    queue.append(neighbor)

    def _find_noise_cave_start(self) -> pg.Vector2 | None:
        """поиск начальной точки пещеры на карте шума (тайла воздуха)
        returns: координаты начальной точки если удалось найти за NOISE_START_SEARCH_TRIES, иначе None"""
        for _ in range(NOISE_START_SEARCH_TRIES):
            # sample some random points on self.vn until find cave
            x, y = random.randint(0, 100), random.randint(0, 100)
            is_cave = self._is_cave_at_pos(pg.Vector2(x, y))
            if is_cave:
                return pg.Vector2(x, y)

        self.debug.increase('cave gen fail: noise start find', 1)
        return None
            
    def _is_cave_at_pos(self, pos: pg.Vector2) -> bool:
        """проверка, является ли данная точка на карте шума воздухом в пещере
        returns: True если воздух, False иначе"""
        # main big caves
        val_main = self.vn.noise(*(pos / self.main_cave_scale))

        # long veins with rotation
        tx = (pos.x * self.cos_vein - pos.y * self.sin_vein) / self.vein_scale_x
        ty = (pos.x * self.sin_vein + pos.y * self.cos_vein) / self.vein_scale_y
        val_veins = self.vn.noise(tx, ty)

        if val_main > self.main_cave_threshold or val_veins > self.vein_threshold:
            return True
        return False

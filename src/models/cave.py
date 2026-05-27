import random
import math
import pygame as pg
from src.settings.base import GroundMaterial
from src.settings.balance import (
    THICKNESS_CONTROL_POINTS_NUM_RANGE, CAVE_LENGTH_RANGE, 
    CAVE_THICKNESS_RANGE, CAVE_MAX_ANGLE_CHANGE, ENEMY_SPAWN_PER_CAVE_RANGE,
    ENEMY_MIN_DISTANCE_FROM_CAVE_START
)

class CaveGenerator:
    """generate caves using random walk algorithm with variable thickness"""
    
    @staticmethod
    def generate_cave(map_obj, start_tile_pos: tuple[int, int], initial_direction: pg.Vector2) -> list[tuple[int, int]]:
        """
        map_obj:  map class to modify
        start_tile_pos:  (x, y) in tile coordinates
        initial_direction:  vector representing the direction of digging
        returns:  list of tile coordinates for enemy spawning
        """
        length = random.randint(*CAVE_LENGTH_RANGE)
        
        # calculating initial angle based on movement direction
        if initial_direction.length_squared() < 0.01:
            angle = random.uniform(0, 360)
        else:
            angle = math.degrees(math.atan2(initial_direction.y, initial_direction.x))
            # Direct it to right or left side
            angle += random.choice((-1,1)) * 60

        current_pos = pg.Vector2(start_tile_pos[0], start_tile_pos[1])
        start_vec = pg.Vector2(start_tile_pos)
        
        # set control points for thickness interpolation
        num_control_points = random.randint(*THICKNESS_CONTROL_POINTS_NUM_RANGE)
        # indices along the path where thickness is defined (excluding start/end)
        if length > 2:
            control_indices = sorted(random.sample(range(1, length - 1), min(num_control_points, length - 2)))
        else:
            control_indices = []
            
        control_indices = [0] + control_indices + [length - 1]
        
        thickness_map = {}
        for idx in control_indices:
            if idx == length - 1 or idx == 0:
                # thin start and end
                thickness_map[idx] = 0.8
            else:
                thickness_map[idx] = random.uniform(*CAVE_THICKNESS_RANGE)

        potential_spawn_tiles = set()

        # generate the path and apply carving
        for i in range(length):
            # calculate interpolated thickness for this step
            thickness = CaveGenerator._get_thickness(i, control_indices, thickness_map)
            # carve tiles around current position
            carved = CaveGenerator._carve_at(map_obj, current_pos, thickness)
            # tiles for enemy spawn ENEMY_MIN_DISTANCE_FROM_CAVE_START far from player
            if i > ENEMY_MIN_DISTANCE_FROM_CAVE_START:
                potential_spawn_tiles.update(carved)
            
            # curving cave
            if random.random() < 0.35:
                # curve max by +-CAVE_MAX_ANGLE_CHANGE degrees along entire length
                angle_change_weighted = CAVE_MAX_ANGLE_CHANGE / num_control_points
                angle += random.uniform(-angle_change_weighted, angle_change_weighted)
            
            # Step forward (in tile units)
            rad = math.radians(angle)
            current_pos += pg.Vector2(math.cos(rad), math.sin(rad))

        if not potential_spawn_tiles:
            return []

        # select random number of enemies
        num_enemies = random.randint(*ENEMY_SPAWN_PER_CAVE_RANGE)
        num_enemies = min(num_enemies, len(potential_spawn_tiles))
        
        spawn_positions = random.sample(list(potential_spawn_tiles), num_enemies)
        return spawn_positions

    @staticmethod
    def _get_thickness(step: int, control_indices: list[int], thickness_map: dict[int, float]) -> float:
        """lerp between control points"""
        if step in thickness_map:
            return thickness_map[step]
        
        for i in range(len(control_indices) - 1):
            idx_start = control_indices[i]
            idx_end = control_indices[i+1]
            if idx_start < step < idx_end:
                t = (step - idx_start) / (idx_end - idx_start)
                return thickness_map[idx_start] + t * (thickness_map[idx_end] - thickness_map[idx_start])
        return 1.0

    @staticmethod
    def _carve_at(map_obj, pos: pg.Vector2, thickness: float) -> list[tuple[int, int]]:
        """
        carves circle of AIR and puts stone borders.
        returns:  list of tiles that were set to air
        """
        air_tiles = []
        check_radius = int(math.ceil(thickness)) + 1
        center_x, center_y = int(round(pos.x)), int(round(pos.y))
        
        for dx in range(-check_radius, check_radius + 1):
            for dy in range(-check_radius, check_radius + 1):
                dist = math.sqrt(dx*dx + dy*dy)
                target_pos = (center_x + dx, center_y + dy)
                
                if dist <= thickness:
                    # inside cave - air
                    map_obj.set_tile_at(target_pos, GroundMaterial.AIR)
                    air_tiles.append(target_pos)
                elif dist <= thickness + 1.2:
                    # cave wall - stone (only if it was unexplored or something else)
                    if not map_obj.is_air(target_pos):
                        map_obj.set_tile_at(target_pos, GroundMaterial.STONE)
        return air_tiles

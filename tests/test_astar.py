import pytest
from src.utils.astar import find_path
from src.settings.base import GroundMaterial

def build_tiles(obstacles, width=5, height=5):
    tiles = {}
    for x in range(width):
        for y in range(height):
            tiles[(x, y)] = GroundMaterial.AIR
    for (x, y) in obstacles:
        tiles[(x, y)] = GroundMaterial.STONE
    return tiles

def test_simple_path():
    tiles = build_tiles([])
    start = (0, 0)
    goal = (2, 2)
    path = find_path(tiles, start, goal)
    assert path[0] == start
    assert path[-1] == goal
    
    assert len(path) == 5

def test_path_with_obstacle():
    obstacles = [(1, 0), (1, 1), (1, 2)]
    tiles = build_tiles(obstacles)
    start = (0, 0)
    goal = (2, 2)
    path = find_path(tiles, start, goal)
    assert path[0] == start
    assert path[-1] == goal
    
    assert len(path) > 5

def test_start_equals_goal():
    tiles = build_tiles([])
    start = (1, 1)
    goal = (1, 1)
    path = find_path(tiles, start, goal)
    assert path == [start]

def test_unreachable_path():
    obstacles = [(2, 1), (1, 2), (2, 3), (3, 2)]
    tiles = build_tiles(obstacles)
    start = (0, 0)
    goal = (2, 2)
    path = find_path(tiles, start, goal)
    
    assert len(path) == 3

from enum import Enum, auto
import pygame as pg

# --- drawing --- 
TILE_SIZE = 20
CAMERA_ZOOM_BASE = 1.0
CAMERA_ZOOM_TILES = 15

# --- window ---
IS_FULLSCREEN = True
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
FPS = 60

# --- world --- 
class ObjectType(Enum):
    # map
    GROUND = auto()
    # entities
    DRONE = auto()
    DRILL = auto()
    ENEMY = auto()
    # misc
    PROJECTILE = auto()

class GroundMaterial(Enum):
    AIR = auto()
    STONE = auto()
    GRAVEL = auto()
    HARD_STONE = auto()

# --- z-index ---
Z_INDEX = {
    ObjectType.GROUND: 0,
    ObjectType.DRILL: 1,
    ObjectType.ENEMY: 2,
    ObjectType.DRONE: 3,
    ObjectType.PROJECTILE: 4,
}

# --- player ---
DRONE_SIZE = (15,15)

class INTENT(Enum):
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    SHOOT = auto()
    MINE = auto()

KEY_TO_INTENT = {
    pg.K_w: INTENT.MOVE_UP,
    pg.K_s: INTENT.MOVE_DOWN,
    pg.K_a: INTENT.MOVE_LEFT,
    pg.K_d: INTENT.MOVE_RIGHT,
    pg.K_SPACE: INTENT.SHOOT,
    pg.K_e: INTENT.MINE,
}

# --- other entities ---
DRILL_SIZE = (TILE_SIZE*9, TILE_SIZE*7)
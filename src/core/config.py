from enum import Enum, auto
import pygame as pg


# --- drawing --- 
TILE_SIZE = 25
CAMERA_ZOOM_BASE = 1.0
CAMERA_ZOOM_TILES = 15


# --- window ---
IS_FULLSCREEN = True
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
FPS = 60


# --- world --- 
SPAWN_SPACE_RADIUS_TILES = 15
SPAWN_SPACE_OFFSET_TILES = (-0.5,-7)

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
DRONE_SIZE = (1.5 * TILE_SIZE, 1.5 * TILE_SIZE)
DRONE_SPAWN_POS = (-DRONE_SIZE[0]//2, -DRONE_SIZE[1]//2)

DRONE_MAX_SPEED = TILE_SIZE * 10
DRONE_ACCELERATION = TILE_SIZE * 1.5
DRONE_DECELERATION = TILE_SIZE * 1

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


# --- drill ---
DRILL_SIZE = (TILE_SIZE*7, TILE_SIZE*15)
DRILL_SPAWN_POS = (-DRILL_SIZE[0]//2, -DRILL_SIZE[1] - 3*TILE_SIZE)
DRILL_SPEED = TILE_SIZE * 1


# --- other entities ---
PROJECTILE_SIZE = (TILE_SIZE//8, TILE_SIZE//8)

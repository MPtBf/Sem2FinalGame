from enum import Enum, auto
import pygame as pg


# --- drawing --- 
TILE_SIZE = 25
CAMERA_ZOOM_BASE = 1.0
CAMERA_ZOOM_TILES = 15


# --- window ---
IS_FULLSCREEN = True
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
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

DRONE_MAX_SPEED = TILE_SIZE * 15
DRONE_ACCELERATION = TILE_SIZE * 1.5
DRONE_DECELERATION = TILE_SIZE * 0.75

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
    pg.K_e: INTENT.MINE,
}


# --- drill ---
DRILL_SIZE = (TILE_SIZE*7, TILE_SIZE*15)
DRILL_SPAWN_POS = (-DRILL_SIZE[0]//2, -DRILL_SIZE[1] - 3*TILE_SIZE)
DRILL_SPEED = TILE_SIZE * 5


# --- other entities ---
PROJECTILE_SIZE = (TILE_SIZE//4, TILE_SIZE//4)
PROJECTILE_SPEED = TILE_SIZE * 25
PROJECTILE_LIFETIME = 10.0
PROJECTILE_INHERIT_PLAYER_VELOCITY = 0.7

ENEMY_SIZE = (TILE_SIZE * 0.8, TILE_SIZE * 0.8)
ENEMY_HEALTH = 50

# multiply velocity by it every frame when collided with the wall. 
# doing that instead of zeroing instantly, to make diagonal movement with collisions smoother
VELOCITY_LOSS_ON_COLLISION = 0.9  


# --- caves ---
CAVE_SPAWN_CHANCE_BASE = 0.05  # 5% base chance
CAVE_MIN_TILES_BETWEEN = 100 # minimum tiles between caves
CAVE_LENGTH_RANGE = (20, 40)
CAVE_THICKNESS_RANGE = (1.5, 3.0)
CAVE_MAX_ANGLE_CHANGE = 30 # degrees
THICKNESS_CONTROL_POINTS_NUM_RANGE = (1,3)
# enemies in caves
ENEMY_SPAWN_PER_CAVE_RANGE = (0,3)
ENEMY_MIN_DISTANCE_FROM_CAVE_START = 15 # in tiles

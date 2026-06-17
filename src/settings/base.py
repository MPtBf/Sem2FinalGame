# core config: window, FPS, tiles, camera, debug, types

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


# --- debug ---
DEBUG_ENABLED = True
DEBUG_SHOW_HITBOXES = False
DEBUG_SHOW_FPS = True
DEBUG_SHOW_STATS = True


# --- world --- 
SPAWN_SPACE_RADIUS_TILES = 15
SPAWN_SPACE_OFFSET_TILES = (-0.5, -7)


# --- enums ---
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


class Intent(Enum):
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    SHOOT = auto()
    MINE = auto()

    PAUSE = auto()
    RESUME = auto()


class ProjectileOwner(Enum):
    PLAYER = auto()
    ENEMY = auto()


class EventType(Enum):
    ENEMY_SPAWN = auto()
    ENEMY_DEATH = auto()
    ENEMY_DAMAGE = auto()

    PLAYER_DEATH = auto()
    PLAYER_DAMAGE = auto()
    PLAYER_COLLECT_RESOURCES = auto()

    GAME_OVER = auto()
    DRILL_DAMAGE = auto()

    PROJECTILE_SPAWN = auto()


class PlayerState(Enum):
    ALIVE = auto()
    RESPAWNING = auto()


# --- input mapping ---
KEY_TO_INTENT = {
    pg.K_w: Intent.MOVE_UP,
    pg.K_s: Intent.MOVE_DOWN,
    pg.K_a: Intent.MOVE_LEFT,
    pg.K_d: Intent.MOVE_RIGHT,
    pg.K_e: Intent.MINE,

    pg.K_p: Intent.PAUSE,
    pg.K_o: Intent.RESUME,
}
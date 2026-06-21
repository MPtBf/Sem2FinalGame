
# visual config: colors, UI positioning, sizes, z-index

import pygame as pg
from enum import Enum, auto
from .base import TILE_SIZE, GroundMaterial, Intent, ItemType, ObjectType


# --- z-index ---
Z_INDEX = {
    ObjectType.GROUND: 0,
    ObjectType.DRILL: 1,
    ObjectType.DRONE: 2,
    ObjectType.ENEMY: 3,
    ObjectType.PROJECTILE: 4,
}


# --- health bar ---
HP_BAR_HEIGHT = 2
HP_BAR_OFFSET_Y = 8
HP_BAR_SCALE_FACTOR = 0.15
HP_BAR_BACKGROUND_COLOR = (0, 0, 0)
HP_BAR_COLOR_HIGH = (255, 120, 0)  # orange
HP_BAR_COLOR_LOW = (120, 0, 0)  # dark red
HP_BAR_FLASH_COLOR = (255, 255, 255)  # white flash on damage
HP_BAR_FLASH_DURATION = 0.2  # seconds

# --- ui ---
PLAYER_RESPAWN_TEXT = 'Дрон уничтожен! Возрождение через:'
SECONDS_TEXT = 'сек'
INVENTORY_TEXT = 'Инвентарь:'
CONTROLS_TEXT = 'Управление:'
PLAYER_RESPAWN_FONT_SIZE = 36
PLAYER_RESPAWN_FONT_COLOR = (255,255,255)
UI_FONT_FAMILY = 'Arial'

# --- overlay ---
INV_OVERLAY_FONT_SIZE = 24

CONTROLS_OVERLAY_FONT_SIZE = 14

OVERLAY_FONT_COLOR = (255,255,255)
OVERLAY_LEFT_MARGIN = OVERLAY_RIGHT_MARGIN = 50
OVERLAY_BOTTOM_MARGIN = 50
OVERLAY_LINES_MARGIN = 10

MINE_SELECTION_COLOR = (255, 255, 255) 
MINE_SELECTION_OPACITY = 80  # 0-255 transparency

# --- language ---
ITEM_TO_TEXT = {
    ItemType.COPPER: 'Медь',
    # ItemType.PATCH: 'Заплатки',
    # ItemType.BULLET: 'Пули',
}
INTENT_TO_TEXT = {
    Intent.MOVE_UP: 'Движение вверх',
    Intent.MOVE_DOWN: 'Движение вниз',
    Intent.MOVE_LEFT: 'Движение влево',
    Intent.MOVE_RIGHT: 'Движение вправо',
    Intent.MINE: 'Добыча блока',
    Intent.HEAL_DRILL: 'Починка бура',
    Intent.TOGGLE_DRILL: 'Вкл/выкл движения бура',

    Intent.PAUSE: 'Пауза',
}

# --- textures & colors ---
OBJECT_TO_TEXTURE_PATH = {
    ObjectType.DRONE: "assets/drone.png",
    ObjectType.DRILL: "assets/drill.png",
    ObjectType.ENEMY: "assets/spider.png",
    ObjectType.GROUND: {
        GroundMaterial.AIR: "assets/air.png",
        GroundMaterial.STONE: "assets/stone.png",
        GroundMaterial.COPPER: "assets/copper.png",
        GroundMaterial.HARD_STONE: "assets/hard_stone.png",
    }
}

DEFAULT_OBJECT_COLORS = {
    ObjectType.DRILL: (200,200,100),
    ObjectType.DRONE: (200,0,200),
    ObjectType.ENEMY: (255, 0, 0),
    ObjectType.PROJECTILE: (255, 255, 0),
    ObjectType.GROUND: {
        GroundMaterial.AIR: (50,50,50),
        GroundMaterial.STONE: (110,110,110),
        GroundMaterial.COPPER: (150,80,50),
        GroundMaterial.HARD_STONE: (150,150,150),
    }
}

BACKGROUND_COLOR = DEFAULT_OBJECT_COLORS[ObjectType.GROUND][GroundMaterial.STONE]

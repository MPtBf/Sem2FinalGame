
# visual config: colors, UI positioning, sizes, z-index

import pygame as pg
from enum import Enum, auto
from .base import TILE_SIZE, Intent, ItemType, ObjectType


# --- z-index ---
Z_INDEX = {
    ObjectType.GROUND: 0,
    ObjectType.DRILL: 1,
    ObjectType.DRONE: 2,
    ObjectType.ENEMY: 3,
    ObjectType.PROJECTILE: 4,
}


# --- health bar ---
HP_BAR_HEIGHT = 4
HP_BAR_OFFSET_Y = 8
HP_BAR_SCALE_FACTOR = 0.1
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

    Intent.PAUSE: 'Пауза',
}
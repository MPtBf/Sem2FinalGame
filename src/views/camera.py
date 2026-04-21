from src.core.config import *
import pygame as pg

class Camera:
    def __init__(self, size: tuple):
        self.offset = pg.Vector2(0, 0)
        self.size = size

    def apply(self, target_pos):
        return target_pos - self.offset

    def update(self, target_entity):
        self.offset.x = target_entity.pos.x - self.size[0] // 2
        self.offset.y = target_entity.pos.y - self.size[1] // 2
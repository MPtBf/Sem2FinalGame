from src.models.game_object import GameObject
from src.settings.base import *
import pygame as pg

class Camera:
    def __init__(self, screen, size: pg.Vector2):
        self.screen = screen
        self.offset = pg.Vector2(0, 0)
        self.size = size

    def apply(self, target_pos):
        return target_pos - self.offset
    
    def world_to_screen_rect(self, world_rect: pg.Rect) -> pg.Rect:
        # converts world coordinates to screen position
        screen_pos = self.apply(pg.Vector2(world_rect.x, world_rect.y))
        return pg.Rect(screen_pos.x, screen_pos.y, world_rect.width, world_rect.height)

    def update(self, target_entity):
        # use float position for smooth tracking
        self.offset.x = target_entity.pos.x + target_entity.size.x / 2 - self.size[0] / 2
        self.offset.y = target_entity.pos.y + target_entity.size.y / 2 - self.size[1] / 2

    def is_obj_in_view(self, object: GameObject):
        return self.rect.colliderect(object.rect)
    
    @property
    def rect(self):
        return pg.Rect(self.offset.x, self.offset.y, self.size.x, self.size.y)

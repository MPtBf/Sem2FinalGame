from src.core.config import DRILL_SIZE, DRONE_SIZE, TILE_SIZE, HP_BAR_HEIGHT, HP_BAR_OFFSET_Y, HP_BAR_SCALE_FACTOR, HP_BAR_BACKGROUND_COLOR, HP_BAR_FILL_COLOR
from src.core.world_handler import World
from .camera import Camera
import pygame as pg
import math
from src.models.game_object import ObjectType, LivingEntity
from src.models.map import GroundMaterial

def temp_image_func(color: tuple):
    def surf_func(size):
        surface = pg.Surface(size)
        surface.fill(color)
        return surface
    return surf_func



class Renderer:
    """class to render everything on the screen"""
    def __init__(self, camera: Camera, world: World, debug=None) -> None:
        self.camera = camera
        self.debug = debug
        # sprites
        self.assets = {
            ObjectType.DRILL: temp_image_func((200,200,100)),
            ObjectType.DRONE: temp_image_func((200,0,200)),
            ObjectType.ENEMY: temp_image_func((255, 0, 0)),
            ObjectType.PROJECTILE: temp_image_func((255, 255, 0)),
            ObjectType.GROUND: {
                GroundMaterial.AIR: temp_image_func((50,50,50)),
                GroundMaterial.STONE: temp_image_func((100,100,100)),
                GroundMaterial.HARD_STONE: temp_image_func((150,150,150)),
            }
        }
        self.world = world

    def render(self, screen):
        screen.fill((0, 0, 0))
        
        # O(1) rendering optimization: get only visible objects from the grid
        visible_objects = self.world.get_visible_objects(self.camera._rect)
        
        if self.debug:
            self.debug.set('rendered_objects', len(visible_objects))
        
        # applying sorting by z-index
        for object in sorted(visible_objects, key=lambda e: e.z_index):
            # checking different ground materials
            sprite = None
            if object.object_type == ObjectType.GROUND:
                ground_assets = self.assets.get(ObjectType.GROUND, {})
                sprite_func = ground_assets.get(object.ground_material)
                sprite = sprite_func(object.size)
            else:
                sprite_func = self.assets.get(object.object_type)
                sprite = sprite_func(object.size)

            screen.blit(sprite, self.camera.apply(object.pos))

        # render health bars for living entities
        for entity in self.world.get_living_entities():
            self._render_health_bar(screen, entity)

    def _render_health_bar(self, screen, entity: LivingEntity):
        health_ratio = entity.health / entity.max_health
        bar_width = entity.max_health**0.5 * HP_BAR_SCALE_FACTOR * TILE_SIZE
        current_width = bar_width * health_ratio
        
        bar_x = entity.pos.x + entity.size.x / 2 - bar_width / 2
        bar_y = entity.pos.y - HP_BAR_OFFSET_Y
        
        screen_pos = self.camera.apply(pg.Vector2(bar_x, bar_y))
        
        # black background
        pg.draw.rect(screen, HP_BAR_BACKGROUND_COLOR, (screen_pos.x, screen_pos.y, bar_width, HP_BAR_HEIGHT))
        # fill health bar
        pg.draw.rect(screen, HP_BAR_FILL_COLOR, (screen_pos.x, screen_pos.y, current_width, HP_BAR_HEIGHT))

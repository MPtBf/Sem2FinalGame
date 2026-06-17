from src.settings.base import TILE_SIZE
from src.settings.visual import (HP_BAR_HEIGHT, HP_BAR_OFFSET_Y, HP_BAR_SCALE_FACTOR, 
                             HP_BAR_BACKGROUND_COLOR, HP_BAR_COLOR_HIGH, HP_BAR_COLOR_LOW, 
                             HP_BAR_FLASH_COLOR, HP_BAR_FLASH_DURATION)
from src.core.world_handler import WorldHandler
from src.views.ui_manager import UIManager
from src.utils.debug_collector import DebugCollector
from .camera import Camera
import pygame as pg
import math
from src.models.game_object import GameObject, ObjectType, LivingEntity
from src.models.map import GroundMaterial

def temp_image_func(color: tuple):
    def surf_func(size):
        surface = pg.Surface(size)
        surface.fill(color)
        return surface
    return surf_func



class Renderer:
    """class to render everything on the screen"""
    def __init__(self, screen, camera: Camera, world_handler: WorldHandler, ui_manager: UIManager, debug: DebugCollector) -> None:
        self.screen = screen
        self.camera = camera
        self.debug = debug
        self.ui_manager = ui_manager
        # sprites
        self.assets = {
            ObjectType.DRILL: temp_image_func((200,200,100)),
            ObjectType.DRONE: temp_image_func((200,0,200)),
            ObjectType.ENEMY: temp_image_func((255, 0, 0)),
            ObjectType.PROJECTILE: temp_image_func((255, 255, 0)),
            ObjectType.GROUND: {
                GroundMaterial.AIR: temp_image_func((50,50,50)),
                GroundMaterial.STONE: temp_image_func((100,100,100)),
                GroundMaterial.COPPER: temp_image_func((150,80,50)),
                GroundMaterial.HARD_STONE: temp_image_func((150,150,150)),
            }
        }
        self.world = world_handler

    def render(self, is_paused):
        self.screen.fill((0, 0, 0))
        
        # rendering optimization: get only visible objects from the grid
        visible_objects = self.world.get_visible_objects(self.camera)
        
        if self.debug:
            self.debug.set('rendered_objects', len(visible_objects))
        
        # applying sorting by z-index
        for object in sorted(visible_objects, key=lambda e: e.z_index):
            if not object.is_visible:
                continue
            # checking different ground materials
            sprite = None
            if object.object_type == ObjectType.GROUND:
                ground_assets = self.assets.get(ObjectType.GROUND, {})
                sprite_func = ground_assets.get(object.ground_material)
                sprite = sprite_func(object.size)
            else:
                sprite_func = self.assets.get(object.object_type)
                sprite = sprite_func(object.size)

            self.screen.blit(sprite, self.camera.apply(object.pos))

        living_entities = self.world.get_living_entities()
        self.ui_manager.render(self.camera, self.world, living_entities)


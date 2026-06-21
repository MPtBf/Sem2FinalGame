from src.settings.balance import OBJECT_TO_SIZE
from src.settings.visual import (BACKGROUND_COLOR, DEFAULT_OBJECT_COLORS, OBJECT_TO_TEXTURE_PATH, Z_INDEX, UI_FONT_FAMILY)
from src.core.world_handler import WorldHandler
from src.views.ui_manager import UIManager
from src.utils.debug_collector import DebugCollector
from .camera import Camera
import pygame as pg
import math
from src.models.game_object import GameObject, ObjectType, LivingEntity
from src.models.map import GroundMaterial


class Renderer:
    """class to render everything on the screen"""
    def __init__(self, screen, camera: Camera, world_handler: WorldHandler, ui_manager: UIManager, debug: DebugCollector) -> None:
        self.screen = screen
        self.camera = camera
        self.debug = debug
        self.ui_manager = ui_manager
        self.world = world_handler
        self.font = pg.font.SysFont(UI_FONT_FAMILY, 48)

        self._setup_images()

    def _setup_images(self):
        self.sprites = {}
        for object_type in ObjectType:
            if object_type == ObjectType.GROUND:
                self.sprites[object_type] = {}
                for material in GroundMaterial: 
                    self.sprites[object_type][material] = self._get_image(object_type, material) 
            else:
                self.sprites[object_type] = self._get_image(object_type)

    def _get_image(self, object_type, ground_material=None):
        if object_type == ObjectType.GROUND:
            image_path = OBJECT_TO_TEXTURE_PATH.get(object_type).get(ground_material)
        else:
            image_path = OBJECT_TO_TEXTURE_PATH.get(object_type)
        size = OBJECT_TO_SIZE[object_type]
        if image_path is None:
            print('no imgae', object_type, ground_material)
            if object_type == ObjectType.GROUND:
                color = DEFAULT_OBJECT_COLORS[object_type][ground_material]
            else:
                color = DEFAULT_OBJECT_COLORS[object_type]
            surface = pg.Surface(size)
            surface.fill(color)
            return surface
        surface = pg.image.load(image_path).convert()
        surface.set_colorkey((255,255,255))
        surface = pg.transform.scale(surface, size)
        return surface


    def render(self, is_paused):
        self.screen.fill(BACKGROUND_COLOR)
        
        # rendering optimization: get only visible objects from the grid
        visible_objects = self.world.get_all_objects_in_rect(self.camera.rect)
        
        if self.debug:
            self.debug.set('rendered_objects', len(visible_objects))
        
        # applying sorting by z-index
        for object in sorted(visible_objects, key=lambda e: Z_INDEX[e.object_type]):
            if issubclass(type(object), LivingEntity) and not object.is_alive():
                continue
            # checking different ground materials
            sprite = None
            if object.object_type == ObjectType.GROUND:
                sprite = self.sprites[ObjectType.GROUND][object.ground_material]
            else:
                sprite = self.sprites[object.object_type]

            self.screen.blit(sprite, self.camera.apply(object.pos))

        living_entities = self.world.get_living_entities()
        self.ui_manager.render(self.camera, self.world, living_entities, is_paused)


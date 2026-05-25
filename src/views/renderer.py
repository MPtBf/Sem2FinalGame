from src.core.config import DRILL_SIZE, DRONE_SIZE, TILE_SIZE
from src.core.world_handler import World
from .camera import Camera
import pygame as pg
from src.models.game_object import ObjectType
from src.models.map import GroundMaterial

def temp_image_func(color: tuple):
    def surf_func(size):
        surface = pg.Surface(size)
        surface.fill(color)
        return surface
    return surf_func



class Renderer:
    """class to render everything on the screen"""
    def __init__(self, camera: Camera) -> None:
        self.camera = camera
        # sprites
        self.assets = {
            ObjectType.DRILL: temp_image_func((200,200,100)),
            ObjectType.DRONE: temp_image_func((200,0,200)),
            ObjectType.ENEMY: temp_image_func((255, 0, 0)),
            ObjectType.GROUND: {
                GroundMaterial.AIR: temp_image_func((50,50,50)),
                GroundMaterial.STONE: temp_image_func((100,100,100)),
                GroundMaterial.HARD_STONE: temp_image_func((150,150,150)),
            }
        }

    def render(self, screen, world: World):
        screen.fill((0, 0, 0))
        
        # O(1) rendering optimization: get only visible objects from the grid
        visible_objects = world.get_visible_objects(self.camera._rect)
        
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

from src.core.config import TILE_SIZE
from src.core.world_handler import World
from .camera import Camera
import pygame as pg
from src.models.game_object import ObjectType
from src.models.map import GroundMaterial

def TempImage(rel_size: tuple, color: tuple):
    surface = pg.Surface([TILE_SIZE * s for s in rel_size])
    surface.fill(color)
    return surface



class Renderer:
    """class to render everything on the screen"""
    def __init__(self, camera: Camera) -> None:
        self.camera = camera
        # sprites
        self.assets = {
            ObjectType.DRILL: TempImage((2, 5), (200,200,100)),
            ObjectType.DRONE: TempImage((0.8, 0.8), (200,0,200)),
            ObjectType.GROUND: {
                GroundMaterial.AIR: TempImage((1, 1), (50,50,50)),
                GroundMaterial.STONE: TempImage((1, 1), (100,100,100)),
                GroundMaterial.GRAVEL: TempImage((1, 1), (200,200,200)),
                GroundMaterial.HARD_STONE: TempImage((1, 1), (150,150,150)),
            }
        }

    def render(self, screen, world: World):
        # applying sorting by z-index
        for entity in sorted(world.get_all_objects(), key=lambda e: e.z_index):
            sprite = None
            # checking different ground materials
            if entity.object_type == ObjectType.GROUND:
                ground_assets = self.assets.get(ObjectType.GROUND, {})
                sprite = ground_assets.get(entity.ground_material)
            else:
                sprite = self.assets.get(entity.object_type)

            screen.blit(sprite, self.camera.apply(entity.pos))

import pygame as pg
from .config import *
from .world_handler import World
from src.views.camera import Camera
from src.views.renderer import Renderer


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pg.time.Clock()
        
        self.world = World() 
        self.camera = Camera(self.screen.get_size())
        self.renderer = Renderer()

        self.is_running = True
        self.dt = 1/FPS

    def _handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

    def run(self):
        while self.is_running:
            self._handle_events()
            
            self.world.update(self.dt)
            
            self.camera.update(self.world.player)
            self.renderer.render(self.screen, self.world, self.camera)

            self.dt = self.clock.tick(FPS) / 1000

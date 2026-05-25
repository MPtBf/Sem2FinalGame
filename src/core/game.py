import pygame as pg
from .config import *
from .world_handler import World
from .input_handler import InputHandler
from .event_bus import EventBus
from src.views.camera import Camera
from src.views.renderer import Renderer


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pg.time.Clock()
        
        self.event_bus = EventBus()
        self.world = World(self.event_bus) 
        self.input_handler = InputHandler()
        self.camera = Camera(self.screen, pg.Vector2(*self.screen.get_size()))
        self.renderer = Renderer(self.camera)

        self.is_running = True
        self.dt = 1/FPS

    def _handle_window_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

    def run(self):
        while self.is_running:
            self._handle_window_events()
            self.input_handler.update()
            intents = self.input_handler.get_intents()
            
            self.world.update(self.dt, intents)
            
            self.camera.update(self.world.drone)
            
            self.renderer.render(self.screen, self.world)
            pg.display.flip()
            
            self.dt = self.clock.tick(FPS) / 1000

import pygame as pg
from .config import *
from .world_handler import World
from .input_handler import InputHandler
from .event_bus import EventBus
from src.views.camera import Camera
from src.views.renderer import Renderer
from src.utils.debug_collector import DebugCollector
from src.views.debug_renderer import DebugRenderer


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pg.time.Clock()

        self.event_bus = EventBus()
        self.debug = DebugCollector() if DEBUG_ENABLED else None
        self.world = World(self.event_bus, self.debug)
        self.input_handler = InputHandler()
        self.camera = Camera(self.screen, pg.Vector2(*self.screen.get_size()))
        self.renderer = Renderer(self.camera, self.world, self.debug)
        self.debug_renderer = DebugRenderer() if DEBUG_ENABLED else None

        self.is_running = True
        self.dt = 1/FPS

    def _handle_window_events(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                self.is_running = False
        return events

    def run(self):
        while self.is_running:
            if self.debug:
                self.debug.set('fps', self.clock.get_fps())
            
            events = self._handle_window_events()
            intents = self.input_handler.get_intents(events, self.camera, self.world.drone)
            
            self.world.update(self.dt, intents)

            self.camera.update(self.world.drone)

            self.renderer.render(self.screen)
            
            if self.debug_renderer:
                entities = [self.world.drone, self.world.drill] + self.world.enemies + self.world.projectiles
                self.debug_renderer.render(self.screen, self.debug, self.camera, entities)
            
            pg.display.flip()

            self.dt = self.clock.tick(FPS) / 1000

import pygame as pg
from src.settings.base import *
from src.views.ui_manager import UIManager
from .world_handler import WorldHandler
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
        self.debug_renderer = DebugRenderer() if DEBUG_ENABLED else None
        self._setup_world()

        self.is_paused = False
        self.game_over = False
        self.is_running = True
        self.dt = 1/FPS

        self.event_bus.subscribe(EventType.GAME_OVER, self._on_game_over)

    def _setup_world(self):
        self.world_handler = WorldHandler(self.event_bus, self.debug)
        self.input_handler = InputHandler()
        self.camera = Camera(self.screen, pg.Vector2(*self.screen.get_size()))
        self.ui_manager = UIManager(self.screen, self.camera)
        self.renderer = Renderer(self.screen, self.camera, self.world_handler, self.ui_manager, self.debug)

    def _on_game_over(self):
        self.game_over = True

    def _on_game_reset(self):
        self.game_over = False
        self._setup_world()

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

            if self.game_over:
                ... # some ui button "start again"
                self._on_game_reset()
            
            events = self._handle_window_events()
            # self.ui_manager.update()  # commented for future logic: UI, menus

            if not (self.is_paused or self.game_over):
                intents = self.input_handler.get_intents(events, self.camera, self.world_handler.drone)

                self.world_handler.update(self.dt, intents)
                self.camera.update(self.world_handler.drone)

            self.renderer.render(self.is_paused)
            
            if self.debug_renderer:
                entities = [self.world_handler.drone, self.world_handler.drill] + self.world_handler.enemies + self.world_handler.projectiles
                self.debug_renderer.render(self.screen, self.debug, self.camera, entities)
            
            pg.display.flip()

            self.dt = self.clock.tick(FPS) / 1000

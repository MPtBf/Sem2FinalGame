import pygame as pg
from src.settings.base import *
from src.views.ui_manager import UIManager
from src.utils.misc import dict_key_from_value
from .world_handler import WorldHandler
from .input_handler import InputHandler
from .event_bus import EventBus
from src.views.camera import Camera
from src.views.renderer import Renderer
from src.utils.debug_collector import DebugCollector
from src.views.debug_renderer import DebugRenderer


class Game:
    """главный класс игры"""    
    def __init__(self):
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pg.FULLSCREEN if IS_FULLSCREEN else 0)
        pg.display.set_caption("<<< Deep Relic >>>")
        self.clock = pg.time.Clock()

        self.event_bus = EventBus()
        self.debug = DebugCollector() if DEBUG_ENABLED else None
        self.debug_renderer = DebugRenderer() if DEBUG_ENABLED else None
        self._setup_world()

        self.is_paused = False
        self.game_over = False
        self.is_running = True
        self.dt = 1/FPS
        self.game_speed = 1.0

        self.event_bus.subscribe(EventType.GAME_OVER, self._on_game_over)

    def _setup_world(self) -> None:
        """установка мира"""
        self.world_handler = WorldHandler(self.event_bus, self.debug)
        self.input_handler = InputHandler()
        self.camera = Camera(self.screen, pg.Vector2(*self.screen.get_size()))
        self.ui_manager = UIManager(self.screen, self.camera)
        self.renderer = Renderer(self.screen, self.camera, self.world_handler, self.ui_manager, self.debug)

    def _on_game_over(self) -> None:
        """обработка события GAME_OVER"""
        self.game_over = True

    def _on_game_reset(self) -> None:
        """обработка события GAME_RESET"""
        self.game_over = False
        self._setup_world()

    def _handle_window_events(self) -> list:
        """обработка и получение списка событий окна.
        returns: список pygame событий"""
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                self.is_running = False
            if event.type == pg.KEYDOWN:
                if event.key == dict_key_from_value(KEY_TO_INTENT, Intent.PAUSE):
                    self.is_paused = not self.is_paused
                if event.key == dict_key_from_value(KEY_TO_INTENT, Intent.SPEED_UP):
                    self.game_speed = SPEED_MULTIPLIER if self.game_speed == 1.0 else 1.0
        return events

    def run(self) -> None:
        """запуск цикла игры"""
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

            self.dt = self.clock.tick(FPS) / 1000 * self.game_speed

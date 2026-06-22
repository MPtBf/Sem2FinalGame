import pygame as pg
from src.settings.base import DEBUG_SHOW_HITBOXES, DEBUG_SHOW_FPS, DEBUG_SHOW_STATS
from src.utils.debug_collector import DebugCollector
from src.views.camera import Camera


class DebugRenderer:
    """отображение информации из DebugCollector на экране"""
    def __init__(self):
        self._font = pg.font.Font(None, 24)
        self._small_font = pg.font.Font(None, 18)
    
    def render(self, screen: pg.Surface, debug: DebugCollector, camera: Camera, entities: list) -> None:
        """отображает информацию из DebugCollector на экране"""
        if DEBUG_SHOW_HITBOXES:
            self._draw_hitboxes(screen, camera, entities)
        
        if DEBUG_SHOW_FPS or DEBUG_SHOW_STATS:
            self._draw_stats(screen, debug)
    
    def _draw_hitboxes(self, screen: pg.Surface, camera: Camera, entities: list):
        for entity in entities:
            if hasattr(entity, 'rect'):
                screen_rect = camera.world_to_screen_rect(entity.rect)
                pg.draw.rect(screen, (0, 255, 0), screen_rect, 1)
    
    def _draw_stats(self, screen: pg.Surface, debug: DebugCollector):
        y_offset = 10
        line_height = 25
        
        stats = debug.get_all()
        
        # FPS отдельно
        if DEBUG_SHOW_FPS and 'fps' in stats:
            fps_text = self._font.render(f"FPS: {stats['fps']:.1f}", True, (255, 255, 0))
            screen.blit(fps_text, (10, y_offset))
            y_offset += line_height
        
        # остальная статистика
        if DEBUG_SHOW_STATS:
            for key, value in sorted(stats.items()):
                if key == 'fps':
                    continue
                
                text = self._small_font.render(f"{key}: {value}", True, (200, 200, 200))
                screen.blit(text, (10, y_offset))
                y_offset += 20

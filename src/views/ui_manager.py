
from math import ceil
import pygame as pg

from src.settings.balance import MINE_REACH_DIST
from src.models.game_object import LivingEntity
from src.core.world_handler import WorldHandler
from src.settings.base import KEY_TO_INTENT, TILE_SIZE, GroundMaterial, PlayerState
from src.settings.visual import MINE_SELECTION_COLOR, MINE_SELECTION_OPACITY
from src.settings.visual import CONTROLS_OVERLAY_FONT_SIZE, CONTROLS_TEXT, HP_BAR_FLASH_DURATION, OVERLAY_BOTTOM_MARGIN, OVERLAY_RIGHT_MARGIN, OVERLAY_BOTTOM_MARGIN, HP_BAR_BACKGROUND_COLOR, HP_BAR_COLOR_HIGH, HP_BAR_COLOR_LOW, HP_BAR_FLASH_COLOR, HP_BAR_HEIGHT, HP_BAR_OFFSET_Y, HP_BAR_SCALE_FACTOR, INTENT_TO_TEXT, OVERLAY_FONT_COLOR, INV_OVERLAY_FONT_SIZE, INVENTORY_TEXT, ITEM_TO_TEXT, OVERLAY_LEFT_MARGIN, OVERLAY_LINES_MARGIN, PLAYER_RESPAWN_FONT_COLOR, PLAYER_RESPAWN_FONT_SIZE, PLAYER_RESPAWN_TEXT, SECONDS_TEXT, UI_FONT_FAMILY
from src.views.camera import Camera
from src.utils.misc import calc_drone_mine_pos



class Button:
    def __init__(self, pos, size, text) -> None:
        self.pos = pos
        self.size = size
        self.text = text

    def update(self, ):
        ...


class UIManager:
    def __init__(self, screen, camera) -> None:
        self.screen = screen
        self.camera = camera
        self.inv_font = pg.font.SysFont(UI_FONT_FAMILY, INV_OVERLAY_FONT_SIZE)
        self.controls_font = pg.font.SysFont(UI_FONT_FAMILY, CONTROLS_OVERLAY_FONT_SIZE)

    def update(self):
        # get mouse pos
        # check buttons for clicks  & emit
        ...

    def _render_player_mine_cursor(self, world_handler: WorldHandler, camera: Camera):
        if world_handler.player_state != PlayerState.ALIVE:
            return
        # calculate world position of mining target
        mine_world_pos = calc_drone_mine_pos(world_handler.drone, camera)
        # tile coordinates
        tile_coords = (int(mine_world_pos.x // TILE_SIZE), int(mine_world_pos.y // TILE_SIZE))
        tile = world_handler.map.get_tile_at(tile_coords)
        if tile is None or tile.ground_material != GroundMaterial.AIR:
            # screen position of tile top‑left
            screen_pos = pg.Vector2(tile_coords) * TILE_SIZE - camera.offset
            # create semi‑transparent overlay surface
            overlay = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
            overlay.fill((*MINE_SELECTION_COLOR, MINE_SELECTION_OPACITY))
            self.screen.blit(overlay, (screen_pos.x, screen_pos.y))
        pg.draw.circle(self.screen, (255,0,0), mine_world_pos - camera.offset, 3)

    def _render_health_bars(self, living_entities: list[LivingEntity]):
        for entity in living_entities:
            if not self.camera.is_obj_in_view(entity):
                continue
            if issubclass(type(object), LivingEntity) and not object.is_alive():
                continue
            
            health_ratio = max(0.0, min(1.0, entity.health / entity.max_health))
            bar_width = entity.max_health**0.5 * HP_BAR_SCALE_FACTOR * TILE_SIZE
            current_width = bar_width * health_ratio
            
            bar_x = entity.pos.x + entity.size.x / 2 - bar_width / 2
            bar_y = entity.pos.y - HP_BAR_OFFSET_Y
            
            screen_pos = self.camera.apply(pg.Vector2(bar_x, bar_y))
            
            # black background
            pg.draw.rect(self.screen, HP_BAR_BACKGROUND_COLOR, (screen_pos.x, screen_pos.y, bar_width, HP_BAR_HEIGHT))
            
            # determine bar color
            if entity.time_drom_last_damage < HP_BAR_FLASH_DURATION:
                # white flash on damage
                bar_color = HP_BAR_FLASH_COLOR
            else:
                # gradient from orange to dark red
                bar_color = (
                    int(HP_BAR_COLOR_HIGH[0] * health_ratio + HP_BAR_COLOR_LOW[0] * (1 - health_ratio)),
                    int(HP_BAR_COLOR_HIGH[1] * health_ratio + HP_BAR_COLOR_LOW[1] * (1 - health_ratio)),
                    int(HP_BAR_COLOR_HIGH[2] * health_ratio + HP_BAR_COLOR_LOW[2] * (1 - health_ratio))
                )
            
            # fill health bar
            pg.draw.rect(self.screen, bar_color, (screen_pos.x, screen_pos.y, current_width, HP_BAR_HEIGHT))

    def render(self, camera, world: WorldHandler, living_entities: list[LivingEntity], is_paused: bool):
        # in-world UI
        self._render_health_bars(living_entities)
        self._render_player_mine_cursor(world, camera)
        # interface UI
        self._render_player_respawn_text(world)
        self._render_player_inventory(world)
        self._render_hotkeys(world)
        if is_paused:
            self._render_pause_text()

    def _render_pause_text(self):
        font = pg.font.SysFont(UI_FONT_FAMILY, 48)
        text_surface = font.render('Пауза. Нажмите P, чтобы продолжить', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text_surface, text_rect)

    def _render_hotkeys(self, world: WorldHandler):
        texts = []
        for key, intent in KEY_TO_INTENT.items():
            text = INTENT_TO_TEXT[intent]
            key_name = pg.key.name(key).upper()
            texts.append(f'{text}: {key_name}')
        texts.append(CONTROLS_TEXT)

        for i, text in enumerate(texts):
            text_surface = self.controls_font.render(text, True, OVERLAY_FONT_COLOR)
            # bottom right
            text_rect = text_surface.get_rect(bottomright=(self.screen.get_width() - OVERLAY_RIGHT_MARGIN, self.screen.get_height() - OVERLAY_BOTTOM_MARGIN - (OVERLAY_LINES_MARGIN + CONTROLS_OVERLAY_FONT_SIZE) * i))
            self.screen.blit(text_surface, text_rect)

    def _render_player_inventory(self, world: WorldHandler):
        texts = []
        for item_type, count in world.drone.inventory.items():
            texts.append(f'{ITEM_TO_TEXT[item_type]}: {round(count,1)}')
        texts.append(INVENTORY_TEXT)

        for i, text in enumerate(texts):
            text_surface = self.inv_font.render(text, True, OVERLAY_FONT_COLOR)
            # bottom left
            text_rect = text_surface.get_rect(topleft=(OVERLAY_LEFT_MARGIN, self.screen.get_height() - OVERLAY_BOTTOM_MARGIN - (OVERLAY_LINES_MARGIN + INV_OVERLAY_FONT_SIZE) * i))
            self.screen.blit(text_surface, text_rect)

    def _render_player_respawn_text(self, world: WorldHandler):
        if world.player_state == PlayerState.RESPAWNING:
            unit_name = SECONDS_TEXT
            respawns_in_int = ceil(world.player_respawns_in)
            text_str = f'{PLAYER_RESPAWN_TEXT} {respawns_in_int} {unit_name}'

            font = pg.font.SysFont(UI_FONT_FAMILY, PLAYER_RESPAWN_FONT_SIZE)
            text_surface = font.render(text_str, True, PLAYER_RESPAWN_FONT_COLOR)
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

            self.screen.blit(text_surface, text_rect)

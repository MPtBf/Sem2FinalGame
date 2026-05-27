import pygame as pg
from src.core.config import INTENT, KEY_TO_INTENT


class InputHandler:
    def get_intents(self, events: list[pg.event.Event], camera, drone) -> dict[INTENT, any]:
        intents = {intent: None for key, intent in KEY_TO_INTENT.items() if pg.key.get_pressed()[key]}
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                world_click = pg.Vector2(event.pos) + camera.offset
                intents[INTENT.SHOOT] = world_click - (drone.pos + drone.size / 2)
        return intents

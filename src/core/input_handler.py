import pygame as pg
from src.settings.base import Intent, KEY_TO_INTENT, MineIntent, ShootIntent
from src.utils.misc import dict_key_from_value


class InputHandler:
    def get_intents(self, events: list[pg.event.Event], camera, drone) -> dict[Intent, any]:
        intents = {intent: None for key, intent in KEY_TO_INTENT.items() if pg.key.get_pressed()[key]}
        if Intent.MINE in intents.keys():
            mouse_pos = pg.Vector2(pg.mouse.get_pos()) + camera.offset 
            payload = MineIntent(mouse_pos=mouse_pos)
            intents[Intent.MINE] = payload
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.Vector2(event.pos) + camera.offset
                direction = mouse_pos - (drone.pos + drone.size / 2)
                payload = ShootIntent(direction=direction)
                intents[Intent.SHOOT] = payload
        return intents

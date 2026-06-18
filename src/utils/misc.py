import pygame as pg

from src.settings.balance import MINE_REACH_DIST


def dict_key_from_value(d, value):
    for k, v in d.items():
        if v == value:
            return k
    return None

def calc_drone_mine_pos(drone, camera):
    mouse_pos = pg.Vector2(pg.mouse.get_pos()) + camera.offset 
    direction = mouse_pos - (drone.pos + drone.size / 2)
    drone_center_pos = drone.pos + drone.size / 2
    direction.scale_to_length(MINE_REACH_DIST)
    return drone_center_pos + direction

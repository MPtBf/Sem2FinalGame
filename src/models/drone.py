import pygame as pg
from .game_object import LivingEntity, ObjectType
from src.core.config import INTENT


class Drone(LivingEntity):
    def __init__(self, pos: pg.Vector2, health):
        super().__init__(pos, ObjectType.DRONE, health)
        self.inventory = {}
        self.speed = 200
        
        self.move_x_map = {INTENT.MOVE_LEFT: -1,
                           INTENT.MOVE_RIGHT: 1,}
        self.move_y_map = {INTENT.MOVE_UP: -1,
                           INTENT.MOVE_DOWN: 1,}
        self.action_map = {
            INTENT.SHOOT: self.shoot,
            INTENT.MINE: self.mine,
        }

    def handle_intents(self, intents):
        self.velocity.x = sum(self.move_x_map.get(intent, 0) for intent in intents)
        self.velocity.y = sum(self.move_y_map.get(intent, 0) for intent in intents)
        # normalizing diagonal movement
        if self.velocity.length() > 0:
            self.velocity.normalize_ip()
            self.velocity *= self.speed
    
        for intent in intents:
            if intent in self.action_map:
                self.action_map[intent]()

    def shoot(self):
        ...

    def mine(self):
        ...

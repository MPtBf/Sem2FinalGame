import pygame as pg
from src.core.config import INTENT, KEY_TO_INTENT


class InputHandler:
    def __init__(self):
        self.keys = {}
    
    def update(self):
        self.keys = pg.key.get_pressed()
    
    def get_intents(self):
        return [KEY_TO_INTENT[key] for key in KEY_TO_INTENT if self.keys[key]]

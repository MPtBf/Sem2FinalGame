import pygame as pg
from src.core.game import Game

def main():
    pg.init()
    game = Game()
    game.run()
    pg.quit()

if __name__ == "__main__":
    main()
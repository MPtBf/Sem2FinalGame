import math
import random

class PerlinNoise:
    def __init__(self, seed: int = None) -> None:
        if seed is None:
            seed = random.randint(0, 1000000000)   
        self.seed = seed

    def get_gradient(self, ix, iy):
        # pseudo-random func
        random_val = math.sin(ix * 12.9898 + iy * 78.233 + self.seed) * 43758.5453
        angle = (random_val - math.floor(random_val)) * 2 * math.pi
        
        return math.cos(angle), math.sin(angle)

    def dot_product(self, grid_x, grid_y, x, y):
        grad_x, grad_y = self.get_gradient(grid_x, grid_y)
        dist_x = x - grid_x
        dist_y = y - grid_y
        return (grad_x * dist_x) + (grad_y * dist_y)

    def fade(self, t):
        return t * t * (3 - 2 * t)

    def lerp(self, a, b, t):
        return a + t * (b - a)

    def noise(self, x, y):
        x0 = math.floor(x)
        x1 = x0 + 1
        y0 = math.floor(y)
        y1 = y0 + 1

        # local pos
        tx = x - x0
        ty = y - y0

        sx = self.fade(tx)
        sy = self.fade(ty)

        # impact of every corner
        n00 = self.dot_product(x0, y0, x, y) 
        n10 = self.dot_product(x1, y0, x, y) 
        n01 = self.dot_product(x0, y1, x, y) 
        n11 = self.dot_product(x1, y1, x, y) 

        ix0 = self.lerp(n00, n10, sx)
        ix1 = self.lerp(n01, n11, sx)
        value = self.lerp(ix0, ix1, sy)

        return value

import math
import random

class PerlinNoise:
    """генератор Perlin-шумов"""
    def __init__(self, seed: int = None) -> None:
        if seed is None:
            seed = random.randint(0, 1000000000)   
        self.seed = seed

    def _get_gradient(self, ix, iy):
        # pseudo-random func
        random_val = math.sin(ix * 12.9898 + iy * 78.233 + self.seed) * 43758.5453
        angle = (random_val - math.floor(random_val)) * 2 * math.pi
        
        return math.cos(angle), math.sin(angle)

    def _dot_product(self, grid_x, grid_y, x, y):
        grad_x, grad_y = self._get_gradient(grid_x, grid_y)
        dist_x = x - grid_x
        dist_y = y - grid_y
        return (grad_x * dist_x) + (grad_y * dist_y)

    def _fade(self, t):
        return t * t * (3 - 2 * t)

    def _lerp(self, a, b, t):
        return a + t * (b - a)

    def noise(self, x, y) -> float:
        """генерирует значение Perlin-шума в точке (x, y)"""
        x0 = math.floor(x)
        x1 = x0 + 1
        y0 = math.floor(y)
        y1 = y0 + 1

        # local pos
        tx = x - x0
        ty = y - y0

        sx = self._fade(tx)
        sy = self._fade(ty)

        # impact of every corner
        n00 = self._dot_product(x0, y0, x, y) 
        n10 = self._dot_product(x1, y0, x, y) 
        n01 = self._dot_product(x0, y1, x, y) 
        n11 = self._dot_product(x1, y1, x, y) 

        ix0 = self._lerp(n00, n10, sx)
        ix1 = self._lerp(n01, n11, sx)
        value = self._lerp(ix0, ix1, sy)

        return value

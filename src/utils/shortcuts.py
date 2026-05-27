from src.settings.base import TILE_SIZE

def TC(x, y=None, revert=False):
    """multiply tile pos by TILE_SIZE to get coordinates
    (Tile pos -> Coordinates)"""
    # handling a thing if someone entered tuple of x,y instead of x
    if y is None:
        x, y = x

    # revert - go from coordinates to tile pos
    mult = TILE_SIZE
    if revert: 
        mult **= -1

    return (*[round(c * mult) for c in (x, y)], )


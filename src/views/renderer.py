

class Renderer:
    def __init__(self) -> None:
        ...

    def render(self, screen, world, camera):
        objects = [world.player, world.drill, world.map] + world.enemies + world.bullets
        for obj in objects:
            ...
            # screen.blit()
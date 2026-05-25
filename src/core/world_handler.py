import pygame as pg
from src.models.game_object import DynamicObject, GameObject
from src.models.drone import Drone
from src.models.drill import Drill
from src.models.enemy import Enemy
from src.models.map import Map
from .config import *

class World:
    def __init__(self):
        self.drone = Drone(
            pg.Vector2(*DRONE_SPAWN_POS), 100
        )
        self.drill = Drill(
            pg.Vector2(*DRILL_SPAWN_POS), 1_000
        )
        self.enemies = []
        self.projectiles = []
        self.map = Map()
        
    def update(self, dt, intents):
        # handle inputs
        self.drone.handle_intents(intents, dt)
        
        # update all dynamic objects
        dynamic_objects = self.get_dynamic_objects()
        
        for obj in dynamic_objects:
            # objects internal logic
            if obj == self.drill:
                self.drill.update_velocity(dt, self.drone)
            elif isinstance(obj, Enemy):...

            # x axis movement and resolution
            obj.move_x(dt)
            if obj == self.drill:
                self.drill.mine(self.map)
                
            if self._resolve_collisions(obj, 'x'):
                obj.sync_pos_to_rect()
                
            # y axis movement and resolution
            obj.move_y(dt)
            if obj == self.drill:
                self.drill.mine(self.map)
                
            if self._resolve_collisions(obj, 'y'):
                obj.sync_pos_to_rect()

        self._manage_entities()

    def get_all_objects(self) -> GameObject:
        return self.enemies + self.projectiles + self.map.get_tiles_list() + \
            [self.drone, self.drill]

    def get_dynamic_objects(self) -> list[DynamicObject]:
        return self.enemies + self.projectiles + [self.drone, self.drill]

    def get_static_objects(self) -> list[GameObject]:
        return self.map.get_tiles_list()

    def _resolve_collisions(self, obj, axis):
        # handle projectiles (they might just die on collision)
        if obj.object_type == ObjectType.PROJECTILE:
            collided_objects = [o for o in self.get_static_objects() if obj.rect.colliderect(o.rect)]
            for wall in collided_objects:
                if wall.ground_material != GroundMaterial.AIR:
                    # simple projectile logic: destroy on hit
                    if hasattr(obj, 'die'):
                        obj.die()
            return False

        # handle collisions for entities
        collided = False
        if obj.object_type in [ObjectType.DRILL, ObjectType.DRONE, ObjectType.ENEMY]:
            collided_objects = [o for o in self.get_static_objects() if obj.rect.colliderect(o.rect)]
            for wall in collided_objects:
                # ignore non-collidable
                if wall.ground_material == GroundMaterial.AIR:
                    continue
                
                collided = True
                if axis == 'x':
                    if obj.velocity.x > 0: # moving right
                        obj.rect.right = wall.rect.left
                    elif obj.velocity.x < 0: # moving left
                        obj.rect.left = wall.rect.right
                    obj.velocity.x = 0
                elif axis == 'y':
                    if obj.velocity.y > 0: # moving down
                        obj.rect.bottom = wall.rect.top
                    elif obj.velocity.y < 0: # moving up
                        obj.rect.top = wall.rect.bottom
                    obj.velocity.y = 0

        return collided
                
        
    def _manage_entities(self):
        ...
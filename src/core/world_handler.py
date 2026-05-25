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
        # update all dynamic objects
        dynamic_objects = self.get_dynamic_objects()
        
        for obj in dynamic_objects:
            # internal logic  (SOLID: delegated to object)
            obj.update_logic(dt, self, intents)

            # X axis movement and resolution
            obj.move_x(dt)
            obj.after_move('x', self)
                
            if self._resolve_collisions(obj, 'x'):
                obj.sync_pos_to_rect()
                
            # Y axis movement and resolution
            obj.move_y(dt)
            obj.after_move('y', self)
                
            if self._resolve_collisions(obj, 'y'):
                obj.sync_pos_to_rect()

        self._manage_entities()

    def get_all_objects(self) -> GameObject:
        return self.enemies + self.projectiles + self.map.get_tiles_list() + \
            [self.drone, self.drill]

    def get_dynamic_objects(self) -> list[DynamicObject]:
        return self.enemies + self.projectiles + [self.drone, self.drill]

    def get_visible_objects(self, view_rect: pg.Rect) -> list[GameObject]:
        # only objects in view_rect, for efficient rendering
        static_visible = self.map.get_tiles_in_rect(view_rect)
        dynamic_visible = [obj for obj in self.get_dynamic_objects() if view_rect.colliderect(obj.rect)]
        return static_visible + dynamic_visible

    def _resolve_collisions(self, obj, axis):
        # handle projectiles (they might just die on collision)
        if obj.object_type == ObjectType.PROJECTILE:
            # O(1) optimization: get only nearby tiles
            collided_objects = self.map.get_tiles_in_rect(obj.rect)
            for wall in collided_objects:
                if wall.ground_material != GroundMaterial.AIR:
                    # simple projectile logic: destroy on hit
                    if hasattr(obj, 'die'):
                        obj.die()
            return False

        # handle collisions for entities
        collided = False
        if obj.object_type in [ObjectType.DRILL, ObjectType.DRONE, ObjectType.ENEMY]:
            # O(1) optimization:  get only nearby tiles
            collided_objects = self.map.get_tiles_in_rect(obj.rect)
            for wall in collided_objects:
                # ignore non-collidable
                if wall.ground_material == GroundMaterial.AIR:
                    continue
                
                # check collision again previous resolution might have pushed us out
                if not obj.rect.colliderect(wall.rect):
                    continue

                collided = True
                if axis == 'x':
                    if obj.velocity.x > 0: # moving right
                        obj.rect.right = wall.rect.left
                    elif obj.velocity.x < 0: # moving left
                        obj.rect.left = wall.rect.right
                elif axis == 'y':
                    if obj.velocity.y > 0: # moving down
                        obj.rect.bottom = wall.rect.top
                    elif obj.velocity.y < 0: # moving up
                        obj.rect.top = wall.rect.bottom
            
            # zero out the velocity
            if collided:
                if axis == 'x':
                    obj.velocity.x *= VELOCITY_LOSS_ON_COLLISION
                else:
                    obj.velocity.y *= VELOCITY_LOSS_ON_COLLISION

        return collided
                
        
    def _manage_entities(self):
        ...
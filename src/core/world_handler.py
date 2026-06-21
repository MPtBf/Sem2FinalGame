import random

import pygame as pg
from src.models.game_object import DynamicObject, GameObject, LivingEntity
from src.models.drone import Drone
from src.models.drill import Drill
from src.models.enemy import Enemy
from src.models.map import Map
from src.models.projectile import Projectile
from src.utils.shortcuts import TC
from src.views.camera import Camera
from .event_bus import EventBus, EventType
from src.settings.base import FPS, ItemType, PlayerState, ObjectType, GroundMaterial, TILE_SIZE, ProjectileOwner
from src.settings.balance import (
    BULLETS_PER_COPPER, DRILL_HP_PER_PATCH, DRILL_HEALTH, DRILL_SPAWN_POS,
    DRONE_SPAWN_POS, ENEMY_SIZE, ENTITY_WEIGHT_MAP, INITIALLY_ALLOCATED_RESOURCES,
    PLAYER_RESPAWN_TIME, PROJECTILE_DAMAGE, SOFT_COLLISION_FORCE,
    VELOCITY_LOSS_ON_COLLISION
)


class WorldHandler:
    def __init__(self, event_bus: EventBus, debug=None):
        self.event_bus = event_bus
        self.debug = debug
        self._setup_drone(pg.Vector2(*DRONE_SPAWN_POS))
        self.drill = Drill(pg.Vector2(*DRILL_SPAWN_POS), event_bus, debug)
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.map = Map(self.event_bus, self.debug)

        self.player_state = PlayerState.ALIVE
        self.player_respawns_in = PLAYER_RESPAWN_TIME
        self.dt = 1 / FPS

        self.event_bus.subscribe(EventType.ENEMY_SPAWN, self._on_enemy_spawn)
        self.event_bus.subscribe(EventType.PLAYER_SHOOT, self._on_player_shoot)
        self.event_bus.subscribe(EventType.PLAYER_DEATH, self._on_player_death)
        self.event_bus.subscribe(EventType.HEAL_DRILL, self._on_player_heal_drill)
        self.event_bus.subscribe(EventType.ENEMY_DEATH, self._on_enemy_death_event)

    def _on_enemy_death_event(self, enemy: Enemy):
        self.enemies.remove(enemy)

    def _setup_drone(self, pos: pg.Vector2):
        self.drone = Drone(pos, self.debug)
        self.drone.inventory = {item: INITIALLY_ALLOCATED_RESOURCES[item] for item in self.drone.inventory}

        self.drone.event_bus = self.event_bus

    def _on_enemy_spawn(self, tile_pos: pg.Vector2):
        world_pos = tile_pos * TILE_SIZE
        # center the enemy on the tile
        center_offset = (pg.Vector2(TILE_SIZE, TILE_SIZE) - pg.Vector2(*ENEMY_SIZE)) / 2
        enemy = Enemy(world_pos + center_offset, self.event_bus)
        self.enemies.append(enemy)

    def _on_player_shoot(self, pos: pg.Vector2, direction: pg.Vector2, shooter_velocity: pg.Vector2):
        # consume bullet (copper for now)
        if self.drone.inventory[ItemType.COPPER] - 1 / BULLETS_PER_COPPER <= 0:
            return False
        self.drone.inventory[ItemType.COPPER] -= 1 / BULLETS_PER_COPPER
        self.projectiles.append(
            Projectile(pos, direction, owner_type=ProjectileOwner.PLAYER, 
            shooter_velocity=shooter_velocity)
        )
        return True

    def _on_player_heal_drill(self):
        if self.drone.inventory[ItemType.COPPER] - 1 <= 0:
            return False
        if not self.drill.rect.colliderect(self.drone.rect):
            return False

        amount = DRILL_HP_PER_PATCH
        if self.drill.health >= DRILL_HEALTH:
            return False

        self.drone.inventory[ItemType.COPPER] -= 1
        self.drill.heal(amount)
        return True

    def _on_player_death(self):
        self.player_state = PlayerState.RESPAWNING

    def _on_player_respawn(self):
        # spawn new drone in the center of a drill
        respawn_pos = self.drill.pos + self.drill.size / 2 - self.drone.size / 2
        self._setup_drone(pg.Vector2(respawn_pos))
        self.player_respawns_in = PLAYER_RESPAWN_TIME
        self.player_state = PlayerState.ALIVE

    def update(self, dt, intents: dict):
        self.dt = dt

        dynamic_objects = self.get_dynamic_objects()

        for obj in dynamic_objects:
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

        if self.debug:
            self.debug.set('player velocity', str(self.drone._velocity))
            self.debug.set('player acceleration', str(self.drone.acceleration))

        self._handle_projectiles()
        self._handle_combat()
        self._resolve_soft_collisions()
        self._manage_entities(dt)
        
        if self.debug:
            self.debug.set('entities', len(dynamic_objects))
            self.debug.set('enemies', len(self.enemies))
            self.debug.set('projectiles', len(self.projectiles))
            self.debug.set('tiles_since_cave', self.map.tiles_mined_since_last_cave)

    def get_all_objects_in_rect(self) -> list[GameObject]:
        return self.enemies + self.projectiles + self.map.get_tiles_list() + [self.drone, self.drill]

    def get_dynamic_objects(self) -> list[DynamicObject]:
        return self.enemies + self.projectiles + [self.drone, self.drill]

    def get_all_objects_in_rect(self, rect) -> list[GameObject]:
        # only objects in rect, for efficient rendering
        static = self.map.get_tiles_in_rect(rect)
        dynamic = [obj for obj in self.get_dynamic_objects() if rect.colliderect(obj.rect)]
        return static + dynamic

    def _resolve_collisions(self, obj, axis):
        # only handle wall collisions physics
        collided = False
        if obj.object_type in (ObjectType.DRILL, ObjectType.DRONE, ObjectType.ENEMY):
            for wall in self.map.get_tiles_in_rect(obj.rect):
                if wall.ground_material == GroundMaterial.AIR:
                    continue
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
            
            # decrease the velocity
            if collided:
                if axis == 'x':
                    obj.velocity.x *= VELOCITY_LOSS_ON_COLLISION
                else:
                    obj.velocity.y *= VELOCITY_LOSS_ON_COLLISION

        return collided

    def _manage_entities(self, dt):
        # remove dead enemies
        self.projectiles = [p for p in self.projectiles if p.alive]

        # player respawn countdown
        if self.player_state == PlayerState.RESPAWNING:
            self.player_respawns_in -= dt
            if self.player_respawns_in <= 0:
                self._on_player_respawn()

    def _handle_projectiles(self):
        # projectile-wall collisions (simple death check)
        for projectile in self.projectiles:
            if not projectile.alive:
                continue
            for wall in self.map.get_tiles_in_rect(projectile.rect):
                if wall.ground_material != GroundMaterial.AIR and projectile.rect.colliderect(wall.rect):
                    projectile.die()
                    break

    def _handle_combat(self):
        # projectile damage
        for projectile in self.projectiles:
            if not projectile.alive:
                continue

            # player projectiles damage enemies
            if projectile.owner_type == ProjectileOwner.PLAYER:
                for enemy in self.enemies:
                    if projectile.rect.colliderect(enemy.rect):
                        knockback_dir = projectile.velocity if projectile.velocity.length() > 0 else None
                        enemy.take_damage(PROJECTILE_DAMAGE, knockback_dir)
                        projectile.die()
                        break

            # enemy projectiles damage player entities
            elif projectile.owner_type == ProjectileOwner.ENEMY:
                for target in [self.drill, self.drone]:
                    if projectile.rect.colliderect(target.rect):
                        knockback_dir = projectile.velocity
                        if knockback_dir.length() == 0:
                            knockback_dir = None
                        target.take_damage(PROJECTILE_DAMAGE, knockback_dir)
                        projectile.die()
                        break

        # drone/drill-enemy contact damage
        for enemy in self.enemies:
            for target in [self.drone, self.drill]:
                if target.rect.colliderect(enemy.rect):
                    drone_center = target.pos + target.size / 2
                    enemy_center = enemy.pos + enemy.size / 2
                    knockback_dir = (drone_center - enemy_center)
                    if knockback_dir.length() == 0:
                        knockback_dir = None

                    is_success = enemy.try_damage(target, knockback_dir)
                    if is_success:
                        enemy.apply_knockback(-knockback_dir)

    def _resolve_soft_collisions(self):
        # push certain entities apart if they overlap
        entities = self.enemies + [self.drill]
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                e1 = entities[i]
                e2 = entities[j]

                if e1.rect.colliderect(e2.rect):
                    # vector between centers
                    c1 = pg.Vector2(e1.rect.center)
                    c2 = pg.Vector2(e2.rect.center)
                    diff = c1 - c2

                    if diff.length() == 0:
                        diff = pg.Vector2(1, 0).angle_to(random.uniform(0, 360))
                    
                    push_dir = diff.normalize()
                    
                    # apply force to both
                    e1_weight = ENTITY_WEIGHT_MAP[e1.object_type]
                    e2_weight = ENTITY_WEIGHT_MAP[e2.object_type]
                    e1.apply_knockback(push_dir, SOFT_COLLISION_FORCE / e1_weight / 2)
                    e2.apply_knockback(-push_dir, SOFT_COLLISION_FORCE / e2_weight / 2)

    def get_living_entities(self) -> list[LivingEntity]:
        return [self.drone, self.drill] + self.enemies

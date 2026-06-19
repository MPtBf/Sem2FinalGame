import pygame as pg
from .game_object import LivingEntity, ObjectType
from src.settings.balance import ENEMY_HEALTH, ENEMY_CONTACT_DAMAGE, ENEMY_DAMAGE_COOLDOWN_SEC, ENEMY_DECELERATION, ENEMY_SIZE, KNOCKBACK_FORCE, ENEMY_MAX_SPEED, ENEMY_ACCELERATION, ENEMY_VISION_RADIUS
from src.settings.base import PlayerState

class Enemy(LivingEntity):
    def __init__(self, pos: pg.Vector2):
        super().__init__(
            pos, 
            pg.Vector2(*ENEMY_SIZE), 
            ObjectType.ENEMY, 
            ENEMY_HEALTH
        )
        self._damage_cooldown = 0.0
        self.acceleration = pg.Vector2(0, 0)

    def update_logic(self, dt, world, intents=None):
        super().update_logic(dt, world, intents)
        if self._damage_cooldown > 0:
            self._damage_cooldown -= dt

        # movement towards nearest of drone (if player alive) or drill
        vec_to_drone = world.drone.pos + world.drone.size/2 - self.pos - self.size/2
        vec_to_drill = world.drill.pos + world.drill.size/2 - self.pos - self.size/2
        dist_to_drone = vec_to_drone.length()
        dist_to_drill = vec_to_drill.length()

        # gather candidate targets (distance, vector) where distance > 0
        candidates = []
        if world.player_state == PlayerState.ALIVE:
            candidates.append((dist_to_drone, vec_to_drone))
        candidates.append((dist_to_drill, vec_to_drill))

        # choose nearest candidate if exist
        if candidates:
            target_dist, target_vec = min(candidates, key=lambda x: x[0])
        else:
            target_dist = float('inf')
            target_vec = pg.Vector2(0, 0)

        # if a valid target is within vision radius, accelerate towards it
        if 0 < target_dist <= ENEMY_VISION_RADIUS:
            # calculate acceleration
            if target_vec.length() > 0:
                direction = target_vec.normalize()
                self.acceleration = direction * ENEMY_ACCELERATION
        else:
            # calculate deceleration
            if self.velocity.length() - self.acceleration.length() > 0:
                self.acceleration = -self.velocity.normalize() * ENEMY_DECELERATION
            else:
                self.acceleration *= 0
                self.velocity *= 0

        self.velocity += self.acceleration

        # limit speed to max speed
        if self.velocity.length() > ENEMY_MAX_SPEED:
            self.velocity.scale_to_length(ENEMY_MAX_SPEED)

    def try_damage(self, target, knockback_direction: pg.Vector2 = None):
        if self._damage_cooldown <= 0:
            target.take_damage(ENEMY_CONTACT_DAMAGE, knockback_direction)
            self._damage_cooldown = ENEMY_DAMAGE_COOLDOWN_SEC
            return True
        return False

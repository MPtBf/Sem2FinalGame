import pygame as pg
from .game_object import LivingEntity, ObjectType
from src.settings.balance import ENEMY_HEALTH, ENEMY_CONTACT_DAMAGE, ENEMY_DAMAGE_COOLDOWN_SEC, ENEMY_DECELERATION, KNOCKBACK_FORCE, ENEMY_MAX_SPEED, ENEMY_ACCELERATION, ENEMY_VISION_RADIUS
from src.settings.visual import ENEMY_SIZE
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

        # movement towards player if within vision radius
        vec_to_player = world.drone.pos + world.drone.size/2 - self.pos - self.size/2
        distance = vec_to_player.length()
        if 0 < distance <= ENEMY_VISION_RADIUS and world.player_state == PlayerState.ALIVE:
            # calculatng acceleation
            if vec_to_player.length() > 0:
                direction = vec_to_player.normalize()
                self.acceleration = direction * ENEMY_ACCELERATION
        # calculatng deceleration
        else:
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

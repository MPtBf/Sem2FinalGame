import pygame as pg
import pygame as pg
import pytest
from src.models.game_object import GameObject, DynamicObject, LivingEntity
from src.settings.base import ObjectType


# Helper subclasses for abstract base classes
class DynamicObjectTest(DynamicObject):
    def update_logic(self, dt, world, intents=None):
        pass

class LivingEntityTest(LivingEntity):
    def die(self):
        self._died = True

# Helper subclasses are not needed for pytest collection; we will use the original classes directly.

def test_gameobject_sync_properties():
    pos = pg.Vector2(5, 5)
    size = pg.Vector2(100, 200)
    obj = GameObject(pos, size, ObjectType.GROUND)
    # initial sync
    assert obj.pos == pos
    assert obj.size == size
    assert obj.rect.topleft == (5, 5)
    assert obj.rect.size == (100, 200)
    
    obj.pos = pg.Vector2(15.7, 25.3)
    assert obj.rect.topleft == (round(15.7), round(25.3))
    
    obj.size = pg.Vector2(50, 75)
    assert obj.rect.size == (50, 75)
    
    assert obj.rect.topleft == (round(15.7), round(25.3))

def test_dynamicobject_movement_and_sync():
    dyn = DynamicObjectTest(pg.Vector2(0, 0), pg.Vector2(10, 10), ObjectType.GROUND, pg.Vector2(3.5, -2.2))
    dyn.move_x(2)
    assert dyn.pos.x == pytest.approx(7.0)
    assert dyn.rect.x == round(dyn.pos.x)
    
    dyn.move_y(3)
    assert dyn.pos.y == pytest.approx(-6.6)
    assert dyn.rect.y == round(dyn.pos.y)

    dyn.rect.topleft = (100, 200)
    dyn.sync_pos_to_rect()
    assert dyn.pos.x == 100
    assert dyn.pos.y == 200

def test_livingentity_is_alive_and_damage():
    le = LivingEntityTest(pg.Vector2(0, 0), pg.Vector2(10, 10), ObjectType.DRONE, health=10)
    assert le.is_alive()
    
    le.take_damage(3)
    assert le.health == 7
    assert le.is_alive()
    
    le.take_damage(10)
    assert le.health <= 0
    assert not le.is_alive()
    
    assert getattr(le, "_died", False)

def test_livingentity_knockback_edge_cases():
    le = LivingEntityTest(pg.Vector2(0, 0), pg.Vector2(10, 10), ObjectType.DRONE, health=10)

    le.take_damage(1, knockback_direction=None)
    assert le._velocity == pg.Vector2(0, 0)
    
    le.take_damage(1, knockback_direction=pg.Vector2(0, 0))
    assert le._velocity == pg.Vector2(0, 0)
    
    dir_vec = pg.Vector2(1, 0)
    le.take_damage(1, knockback_direction=dir_vec)
    assert le._velocity.length() > 0

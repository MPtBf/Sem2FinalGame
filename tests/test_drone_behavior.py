import pygame as pg
import pytest
from unittest.mock import MagicMock

from src.models.drone import Drone
from src.settings.base import Intent, ShootIntent, MineIntent
from src.settings.balance import DRONE_MAX_SPEED, DRONE_ACCELERATION, DRONE_DECELERATION, MINE_REACH_DIST
from src.core.event_bus import EventType

# Helper to create a Drone with mocked dependencies

def make_drone():
    pg.init()
    drone = Drone(pos=pg.Vector2(0, 0), debug=MagicMock())
    drone.event_bus = MagicMock()
    return drone

@pytest.fixture
def mock_map():
    return MagicMock()

def test_acceleration_applies_correctly():
    drone = make_drone()
    drone.update_logic(1, MagicMock(), {Intent.MOVE_RIGHT: None})
    assert drone.acceleration.x == pytest.approx(DRONE_ACCELERATION)
    assert drone.acceleration.y == 0
    assert drone._velocity.x == pytest.approx(DRONE_ACCELERATION)
    assert drone._velocity.y == 0

def test_speed_clamped_to_max():
    drone = make_drone()
    for _ in range(30):
        drone.update_logic(1, MagicMock(), {Intent.MOVE_RIGHT: None})
    assert drone._velocity.length() <= DRONE_MAX_SPEED

def test_deceleration_to_zero():
    drone = make_drone()
    drone.update_logic(1, MagicMock(), {Intent.MOVE_RIGHT: None})
    for _ in range(30):
        drone.update_logic(1, MagicMock(), {})
        if drone._velocity.length() == 0:
            break
    assert drone._velocity.length() == 0
    assert drone.acceleration.length() == 0

# shoot

def test_shoot_emits_event():
    drone = make_drone()
    payload = ShootIntent(direction=pg.Vector2(1, 0))
    drone._handle_intents({Intent.SHOOT: payload}, world=MagicMock())
    drone.event_bus.emit.assert_called_once()
    args, kwargs = drone.event_bus.emit.call_args
    assert args[0] == EventType.PLAYER_SHOOT
    expected_pos = drone.pos + drone.size / 2
    assert kwargs['pos'].x == pytest.approx(expected_pos.x)
    assert kwargs['pos'].y == pytest.approx(expected_pos.y)
    assert kwargs['direction'] == payload.direction
    assert kwargs['shooter_velocity'] == pg.Vector2(drone._velocity)

def test_shoot_with_zero_velocity():
    drone = make_drone()
    payload = ShootIntent(direction=pg.Vector2(0, -1))
    drone._handle_intents({Intent.SHOOT: payload}, world=MagicMock())
    _, kwargs = drone.event_bus.emit.call_args
    assert kwargs['shooter_velocity'].length() == 0

# mine

def test_mine_calls_map(mock_map):
    drone = make_drone()
    mouse_pos = pg.Vector2(100, 100)
    payload = MineIntent(mouse_pos=mouse_pos)
    drone._handle_intents({Intent.MINE: payload}, world=MagicMock(map=mock_map))
    args, _ = mock_map.mine.call_args
    direction = args[1]
    assert direction.length() == pytest.approx(MINE_REACH_DIST)

# heal drill

def test_heal_drill_emits_once():
    drone = make_drone()
    drone._handle_intents({Intent.HEAL_DRILL: None}, world=MagicMock())
    drone.event_bus.emit.assert_called_once_with(EventType.HEAL_DRILL)
    drone.event_bus.emit.reset_mock()
    drone._handle_intents({Intent.HEAL_DRILL: None}, world=MagicMock())
    drone.event_bus.emit.assert_not_called()
    drone._handle_intents({}, world=MagicMock())
    drone._handle_intents({Intent.HEAL_DRILL: None}, world=MagicMock())
    drone.event_bus.emit.assert_called_once_with(EventType.HEAL_DRILL)

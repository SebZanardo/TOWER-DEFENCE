from dataclasses import dataclass
from enum import Enum, auto

from constants import DT
from field import (
    Position,
    Field,
    FlowField,
    Direction,
    Tile,
    inside_field,
    recalculate_flow_field,
)
from enemy import EnemyList, Enemy
from player import Player


class TowerType(Enum):
    BASIC = auto()
    HEAVY = auto()
    SPEEDY = auto()


# Tuple format: (BUY_VALUE, SELL_VALUE, RANGE, RELOAD_SPEED, DAMAGE)
TOWER_STATS_TABLE: dict[TowerType, tuple] = {
    TowerType.BASIC: (3, 2, 2.5, 0.1, 0.2),
    TowerType.HEAVY: (20, 15, 6.0, 0.2, 1),
    TowerType.SPEEDY: (10, 5, 3.5, 0.025, 0.3),
}

TOWER_RANGE_SQUARED: dict[TowerType, float] = {
    tower_type: TOWER_STATS_TABLE[tower_type][2] ** 2 for tower_type in list(TowerType)
}


@dataclass
class Tower:
    tower_type: TowerType
    buy_value: int
    sell_value: int
    range: float
    reload_speed: float
    damage: float

    target: Enemy = None
    reload_timer: float = 0


# Typehints
TowerMap = dict[Position, Tower]


def place_tower(
    x: int,
    y: int,
    tower_type: TowerType,
    field: Field,
    tower_map: TowerMap,
    player: Player,
) -> None:
    stats = TOWER_STATS_TABLE[tower_type]
    tower = Tower(tower_type, *stats)

    # Deduct price from player money
    player.money -= tower.buy_value

    tower_map[(x, y)] = tower
    field[y][x] = Tile.TOWER


# NOTE: Only call valid_tower_tile on frame if (x, y) changes or field has changed
def valid_tower_tile(
    x: int,
    y: int,
    field: Field,
    flow_field: FlowField,
    start: Position,
    end: Position,
) -> bool:
    if not inside_field(x, y):
        return False

    if (x, y) == start or (x, y) == end:
        return False

    tile = field[y][x]
    if tile != Tile.EMPTY:
        return False

    field[y][x] = Tile.TOWER
    valid = recalculate_flow_field(field, flow_field, start, end)
    field[y][x] = tile

    return valid


def is_tower_on_enemy(
    x: int, y: int, field: Field, flow_field: FlowField, enemies: EnemyList
) -> bool:
    # Tile should always be Tile.EMPTY because valid_tower_tile should be called first as it is less intensive
    tile = field[y][x]
    field[y][x] = Tile.TOWER

    valid = True

    # Test if placing tower ontop of an enemy
    cleared = set()
    for enemy in enemies:
        position = (enemy.last_x, enemy.last_y)

        # Already cleared so skip
        if position in cleared:
            continue

        # Test is last (x, y) has a move direction
        if flow_field[enemy.last_y][enemy.last_x] == Direction.NONE:
            if enemy.percent_travelled < 0.5:
                valid = False
                break
            if flow_field[enemy.next_y][enemy.next_x] == Direction.NONE:
                valid = False
                break

        # Add to cleared
        cleared.add(position)

    field[y][x] = tile

    return valid


def update_towers(tower_map: TowerMap, enemies: EnemyList) -> None:
    for tower_position, tower in tower_map.items():
        # If tower has no target find a target
        if tower.target is None:
            find_new_target(*tower_position, tower, enemies)

        # Check if still in range or dead
        else:
            if tower.target.health <= 0 or not in_range(
                *tower_position,
                tower.target.x,
                tower.target.y,
                TOWER_RANGE_SQUARED[tower.tower_type]
            ):
                tower.target = None
                find_new_target(*tower_position, tower, enemies)

        tower.reload_timer -= DT

        # Deal damage
        if tower.target is not None and tower.reload_timer <= 0:
            tower.target.health -= tower.damage
            tower.reload_timer = tower.reload_speed


def find_new_target(
    tower_x: int, tower_y: int, tower: Tower, enemies: EnemyList
) -> bool:
    for enemy in enemies:
        # Found a target
        if in_range(
            tower_x, tower_y, enemy.x, enemy.y, TOWER_RANGE_SQUARED[tower.tower_type]
        ):
            tower.target = enemy
            break


def in_range(
    tower_x: int, tower_y: int, enemy_x: int, enemy_y: int, range_squared: float
) -> bool:
    distance_squared = (tower_x - enemy_x) ** 2 + (tower_y - enemy_y) ** 2
    return distance_squared <= range_squared

from dataclasses import dataclass
from enum import Enum, auto

from field import OPPOSITE_DIRECTION, Position, FlowField, Direction
from player import Player


class EnemyType(Enum):
    BASIC = auto()
    HEAVY = auto()
    SPEEDY = auto()


# Tuple format: (HEALTH, SPEED, DAMAGE, VALUE)
# Ideal if SPEED is a unit fraction to stop running past tile
ENEMY_STATS_TABLE: dict[EnemyType, tuple] = {
    EnemyType.BASIC: (10, 0.025, 1, 1),
    EnemyType.HEAVY: (50, 0.025, 2, 2),
    EnemyType.SPEEDY: (30, 0.05, 1, 1),
}


@dataclass
class Enemy:
    enemy_type: EnemyType
    health: float
    speed: float
    damage: int
    value: int

    # Need to store last tile position incase tower placed on next tile.
    # To resolve this case nicely, flip move direction, next = last, last = next
    # Re-assign last, next and move_direction when reaching next
    last_x: int
    last_y: int
    next_x: int
    next_y: int

    # Easy to calculate rendering from this
    x: float
    y: float

    # For sprite drawing and has reached target checks
    move_direction: Direction

    # To see if enemy is at next square yet
    # Also for placing towers when enemy has left last square
    percent_travelled: float = 0


# Typehints
EnemyList = list[Enemy]


def spawn_enemy(
    spawn: Position, enemy_type: EnemyType, enemies: EnemyList, flow_field: FlowField
) -> None:
    stats = ENEMY_STATS_TABLE[enemy_type]
    direction = flow_field[spawn[1]][spawn[0]]
    next_tile = (spawn[0] + direction.value[0], spawn[1] + direction.value[1])

    enemies.append(Enemy(enemy_type, *stats, *spawn, *next_tile, *spawn, direction))


def handle_enemies_backtracking(enemies: EnemyList, flow_field: FlowField) -> None:
    # Iterate over all enemies and handle running backwards cases
    for enemy in enemies:
        if (
            flow_field[enemy.last_y][enemy.last_x] != enemy.move_direction
            and flow_field[enemy.last_y][enemy.last_x] != Direction.NONE
        ):
            temp_x = enemy.last_x
            temp_y = enemy.last_y
            enemy.last_x = enemy.next_x
            enemy.last_y = enemy.next_y
            enemy.next_x = temp_x
            enemy.next_y = temp_y
            enemy.move_direction = OPPOSITE_DIRECTION[enemy.move_direction]
            enemy.percent_travelled = 1 - enemy.percent_travelled


def update_enemies(
    enemies: EnemyList, player: Player, flow_field: FlowField, end: Position
) -> None:
    # Update enemies (Loop through backwards so I can remove them if dead)
    for i in range(len(enemies) - 1, -1, -1):
        enemy = enemies[i]

        # Check if enemy is dead
        if enemy.health <= 0:
            # Add value to player money
            player.money += enemy.value
            enemies.pop(i)
            continue

        # Move
        enemy.x += enemy.move_direction.value[0] * enemy.speed
        enemy.y += enemy.move_direction.value[1] * enemy.speed
        enemy.percent_travelled += enemy.speed

        # Check if enemy has made it to the next_tile
        if enemy.percent_travelled >= 1:
            # Set x and y to position incase speed was not unit fraction
            enemy.x = enemy.next_x
            enemy.y = enemy.next_y

            # Check to see if enemy has reached the end tile
            if enemy.x == end[0] and enemy.y == end[1]:
                # Deal damage to player health
                player.health -= enemy.damage
                enemy.health = 0
                enemies.pop(i)
                continue

            enemy.last_x = enemy.next_x
            enemy.last_y = enemy.next_y
            enemy.move_direction = flow_field[enemy.y][enemy.x]
            enemy.next_x = enemy.x + enemy.move_direction.value[0]
            enemy.next_y = enemy.y + enemy.move_direction.value[1]
            enemy.percent_travelled = 0

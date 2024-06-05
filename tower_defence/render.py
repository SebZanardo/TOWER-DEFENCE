import pygame

from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from field import (
    FIELD_WIDTH,
    FIELD_HEIGHT,
    TILE_SIZE,
    TILE_SIZE_TUPLE,
    HALF_TILE_SIZE,
    Position,
    Field,
    FlowField,
    Tile,
    Direction,
)
from tower import TowerMap, TowerType
from player import Player
from enemy import EnemyList, EnemyType


# Positioning offsets
FIELD_OFFSET_X = (WINDOW_WIDTH - FIELD_WIDTH * TILE_SIZE) // 2
FIELD_OFFSET_Y = (WINDOW_HEIGHT - FIELD_HEIGHT * TILE_SIZE) // 2

# Colour Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)

GREY = (100, 100, 100)
DARK_GREY = (50, 50, 50)
LIGHT_GREY = (150, 150, 150)

EMPTY_TILE_LIGHT_COLOUR = GREEN
EMPTY_TILE_DARK_COLOUR = (0, 200, 0)
BLOCKED_TILE_COLOUR = CYAN
WALKABLE_TILE_COLOUR = LIGHT_GREY
TOWER_TILE_COLOUR = GREY


LINE_WIDTH = TILE_SIZE // 8
HALF_LINE_WIDTH = LINE_WIDTH // 2


def get_screen_tile_corner(x: int, y: int) -> Position:
    return (
        x * TILE_SIZE + FIELD_OFFSET_X,
        y * TILE_SIZE + FIELD_OFFSET_Y,
    )


def get_screen_tile_center(x: int, y: int) -> Position:
    return (
        x * TILE_SIZE + HALF_TILE_SIZE + FIELD_OFFSET_X,
        y * TILE_SIZE + HALF_TILE_SIZE + FIELD_OFFSET_Y,
    )


def render_field(surface: pygame.Surface, field: Field) -> None:
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            tile = field[y][x]
            tile_rect = (get_screen_tile_corner(x, y), TILE_SIZE_TUPLE)
            match (tile):
                case Tile.EMPTY:
                    if (x + y) % 2 == 0:
                        tile_colour = EMPTY_TILE_LIGHT_COLOUR
                    else:
                        tile_colour = EMPTY_TILE_DARK_COLOUR
                case Tile.TOWER:
                    tile_colour = TOWER_TILE_COLOUR
                case Tile.WALKABLE:
                    tile_colour = WALKABLE_TILE_COLOUR
                case Tile.BLOCKED:
                    tile_colour = BLOCKED_TILE_COLOUR
                case _:
                    tile_colour = MAGENTA

            pygame.draw.rect(surface, tile_colour, tile_rect)


def render_flow_field(
    surface: pygame.Surface, font: pygame.Font, flow_field: FlowField
) -> None:
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            direction = flow_field[y][x]
            string = "None" if direction == Direction.NONE else str(direction.value)
            text = font.render(string, True, BLACK)

            surface.blit(text, get_screen_tile_corner(x, y))


def render_enemies(surface: pygame.Surface, enemies: EnemyList) -> None:
    for enemy in enemies:
        enemy_center = get_screen_tile_center(enemy.x, enemy.y)

        match (enemy.enemy_type):
            case EnemyType.BASIC:
                colour = LIGHT_GREY
                radius = TILE_SIZE // 4
            case EnemyType.HEAVY:
                colour = BLUE
                radius = TILE_SIZE // 2
            case EnemyType.SPEEDY:
                colour = RED
                radius = TILE_SIZE // 4
            case _:
                colour = MAGENTA
                radius = TILE_SIZE // 2

        pygame.draw.circle(surface, colour, enemy_center, radius, LINE_WIDTH)


def render_towers(surface: pygame.Surface, tower_map: TowerMap) -> None:
    for tower_position, tower in tower_map.items():
        tile_center = get_screen_tile_center(*tower_position)

        match (tower.tower_type):
            case TowerType.BASIC:
                colour = LIGHT_GREY
            case TowerType.HEAVY:
                colour = BLUE
            case TowerType.SPEEDY:
                colour = RED
            case _:
                colour = MAGENTA

        pygame.draw.circle(surface, colour, tile_center, HALF_TILE_SIZE, LINE_WIDTH)


def render_tower_targets(surface: pygame.Surface, tower_map: TowerMap) -> None:
    for tower_position, tower in tower_map.items():
        if tower.target is None:
            continue

        start_pos = get_screen_tile_center(*tower_position)
        end_pos = get_screen_tile_center(tower.target.x, tower.target.y)

        if tower.reload_timer == tower.reload_speed:
            colour = YELLOW
        else:
            colour = GREY

        pygame.draw.line(surface, colour, start_pos, end_pos, LINE_WIDTH)


def render_tower_range(
    transparent_surface: pygame.Surface, x: int, y: int, tower_map: TowerMap
) -> None:
    tower = tower_map[(x, y)]
    pygame.draw.circle(
        transparent_surface,
        WHITE,
        get_screen_tile_center(x, y),
        tower.range * TILE_SIZE,
        HALF_LINE_WIDTH,
    )


def render_player_stats(
    surface: pygame.Surface, font: pygame.Font, player: Player
) -> None:
    health_text = font.render(f"♥{player.health}", True, RED)
    money_text = font.render(f"${player.money}", True, YELLOW)
    surface.blit(health_text, (0, 0))
    surface.blit(money_text, (0, 660))


def render_preview(
    transparent_surface: pygame.Surface, x: int, y: int, valid_placement: bool
) -> None:
    tile_center = get_screen_tile_center(x, y)
    if valid_placement:
        pygame.draw.circle(
            transparent_surface, GREY, tile_center, HALF_TILE_SIZE, LINE_WIDTH
        )
    else:
        pygame.draw.circle(
            transparent_surface, RED, tile_center, HALF_TILE_SIZE, LINE_WIDTH
        )


def render_shortest_path(
    transparent_surface: pygame.Surface, flow_field: FlowField, start: Position
) -> None:
    x, y = start
    tile_from = get_screen_tile_center(x, y)
    while True:
        direction = flow_field[y][x]

        if direction == Direction.NONE:
            break  # There is no more path

        x += direction.value[0]
        y += direction.value[1]

        tile_to = get_screen_tile_center(x, y)
        pygame.draw.line(transparent_surface, YELLOW, tile_from, tile_to, LINE_WIDTH)
        tile_from = tile_to

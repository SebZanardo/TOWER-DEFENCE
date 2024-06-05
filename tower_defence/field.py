from collections import deque
from enum import Enum, auto


FIELD_WIDTH = 20
FIELD_HEIGHT = 11
TILE_SIZE = 48
TILE_SIZE_TUPLE = (TILE_SIZE, TILE_SIZE)
HALF_TILE_SIZE = TILE_SIZE // 2


class Tile(Enum):
    EMPTY = auto()
    TOWER = auto()
    WALKABLE = auto()
    BLOCKED = auto()


class Direction(Enum):
    NONE = (0, 0)
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)
    NORTH_EAST = (1, -1)
    NORTH_WEST = (-1, -1)
    SOUTH_EAST = (1, 1)
    SOUTH_WEST = (-1, 1)


OPPOSITE_DIRECTION: dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST,
    Direction.NORTH_EAST: Direction.SOUTH_WEST,
    Direction.NORTH_WEST: Direction.SOUTH_EAST,
    Direction.SOUTH_EAST: Direction.NORTH_WEST,
    Direction.SOUTH_WEST: Direction.NORTH_EAST,
}


FLOW_FIELD_DIRECTIONS: tuple[Direction] = (
    Direction.EAST,
    Direction.NORTH,
    Direction.SOUTH,
    Direction.WEST,
)


# Typehints
Position = tuple[int, int]
Field = list[list[Tile]]
FlowField = list[list[Direction]]


def inside_field(x: int, y: int) -> bool:
    return x >= 0 and x < FIELD_WIDTH and y >= 0 and y < FIELD_HEIGHT


# NOTE: Needs to be called whenever field changes
def recalculate_flow_field(
    field: Field, flow_field: FlowField, start: Position, end: Position
) -> bool:
    # Clear the flow field
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            flow_field[y][x] = Direction.NONE

    # Flow starts at end and flood fills until every empty tile is visited
    visited_tiles = set()
    queue = deque()
    queue.append(end)
    visited_tiles.add(end)

    while queue:
        x, y = queue.popleft()
        for direction in FLOW_FIELD_DIRECTIONS:
            new_x = x + direction.value[0]
            new_y = y + direction.value[1]

            if not inside_field(new_x, new_y):
                continue

            if field[new_y][new_x] == Tile.BLOCKED or field[new_y][new_x] == Tile.TOWER:
                continue

            new_tile = (new_x, new_y)
            if new_tile in visited_tiles:
                continue

            queue.append(new_tile)
            visited_tiles.add(new_tile)
            flow_field[new_y][new_x] = OPPOSITE_DIRECTION[direction]

    return flow_field[start[1]][start[0]] is not Direction.NONE

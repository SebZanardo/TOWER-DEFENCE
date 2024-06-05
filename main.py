import pygame
import random

from constants import (
    RESOLUTION,
    FPS,
    COLOR_KEY,
)
from render import FIELD_OFFSET_X, FIELD_OFFSET_Y, BLACK
from field import (
    FIELD_WIDTH,
    FIELD_HEIGHT,
    TILE_SIZE,
    Position,
    Field,
    FlowField,
    Direction,
    Tile,
    recalculate_flow_field,
    inside_field,
)
from tower import (
    TowerMap,
    TowerType,
    valid_tower_tile,
    is_tower_on_enemy,
    place_tower,
    update_towers,
)
from enemy import (
    EnemyList,
    EnemyType,
    handle_enemies_backtracking,
    spawn_enemy,
    update_enemies,
)
from player import Player, STARTING_HEALTH, STARTING_MONEY
from render import (
    render_enemies,
    render_field,
    render_flow_field,
    render_player_stats,
    render_preview,
    render_shortest_path,
    render_towers,
    render_tower_range,
    render_tower_targets,
)


pygame.init()

window = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("TOWER DEFENCE")
clock = pygame.time.Clock()

transparent_surface = pygame.Surface(RESOLUTION)
transparent_surface.set_alpha(150)
transparent_surface.set_colorkey(COLOR_KEY)

font = pygame.font.SysFont("sfprodisplayblack", 10)
font_big = pygame.font.SysFont("sfprodisplayblack", 30)


def main() -> None:
    player: Player = Player(STARTING_HEALTH, STARTING_MONEY)
    tower_map: TowerMap = {}
    enemies: EnemyList = []

    start: Position = (0, FIELD_HEIGHT // 2)
    end: Position = (FIELD_WIDTH - 1, FIELD_HEIGHT // 2)
    field: Field = [
        [Tile.EMPTY for x in range(FIELD_WIDTH)] for y in range(FIELD_HEIGHT)
    ]
    flow_field: FlowField = [
        [Direction.NONE for x in range(FIELD_WIDTH)] for y in range(FIELD_HEIGHT)
    ]
    preview_flow_field: FlowField = [
        [Direction.NONE for x in range(FIELD_WIDTH)] for y in range(FIELD_HEIGHT)
    ]

    last_preview_x = -1
    last_preview_y = -1
    valid_tile = False

    # TODO: Set when dragging (Mouse down to select tower type then release to place)
    # And set with numbers on keyboard
    selected_tower_type = TowerType.BASIC

    recalculate_flow_field(field, flow_field, start, end)

    while True:
        ### INPUT ###
        mouse_position = pygame.mouse.get_pos()
        mouse_clicked = False
        spawn_new_enemy = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                if event.key == pygame.K_SPACE:
                    spawn_new_enemy = True
                if event.unicode.isdigit():
                    match (event.unicode):
                        case "1":
                            selected_tower_type = TowerType.BASIC
                        case "2":
                            selected_tower_type = TowerType.HEAVY
                        case "3":
                            selected_tower_type = TowerType.SPEEDY

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_clicked = True

        ### LOGIC ###
        # TODO: Add logic so can't purchase tower if not enough money

        # Preview placement
        preview_x = (mouse_position[0] - FIELD_OFFSET_X) // TILE_SIZE
        preview_y = (mouse_position[1] - FIELD_OFFSET_Y) // TILE_SIZE

        if preview_x != last_preview_x or preview_y != last_preview_y:
            valid_tile = valid_tower_tile(
                preview_x, preview_y, field, preview_flow_field, start, end
            )
            last_preview_x = preview_x
            last_preview_y = preview_y

        valid_placement = False
        if valid_tile:
            valid_placement = is_tower_on_enemy(
                preview_x, preview_y, field, preview_flow_field, enemies
            )

        # Place tower
        if mouse_clicked and valid_placement:
            place_tower(
                preview_x, preview_y, selected_tower_type, field, tower_map, player
            )
            recalculate_flow_field(field, flow_field, start, end)
            handle_enemies_backtracking(enemies, flow_field)
            valid_tile = False

        # TODO: Add inspecting tower (show range, upgrade, sell)

        # Spawn enemy
        if spawn_new_enemy:
            spawn_enemy(start, random.choice(list(EnemyType)), enemies, flow_field)

        update_enemies(enemies, player, flow_field, end)
        update_towers(tower_map, enemies)

        ### RENDERING ###
        window.fill(BLACK)
        transparent_surface.fill(COLOR_KEY)

        render_field(window, field)
        render_enemies(window, enemies)
        render_towers(window, tower_map)
        render_tower_targets(window, tower_map)


        if valid_placement:
            # render_flow_field(window, font, preview_flow_field)
            render_shortest_path(transparent_surface, preview_flow_field, start)
        else:
            # render_flow_field(window, font, flow_field)
            render_shortest_path(transparent_surface, flow_field, start)

        if inside_field(preview_x, preview_y):
            if field[preview_y][preview_x] == Tile.TOWER:
                render_tower_range(transparent_surface, preview_x, preview_y, tower_map)
            else:
                render_preview(transparent_surface, preview_x, preview_y, valid_placement)

        render_player_stats(window, font_big, player)

        window.blit(transparent_surface, (0, 0))

        clock.tick(FPS)
        pygame.display.flip()


def terminate() -> None:
    pygame.quit()
    raise SystemExit


if __name__ == "__main__":
    main()

import tcod
import tcod.map

from game_map import GameMap


def initialize_fov(game_map: GameMap) -> tcod.map.Map:
    fov_map = tcod.map_new(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            tcod.map_set_properties(fov_map, x, y,
                                    not game_map.tiles[x][y].block_sight,
                                    not game_map.tiles[x][y].blocked)

    return fov_map


def recompute_fov(fov_map: tcod.map.Map, x: int, y: int, radius: int,
                  light_walls: bool = True, algorithm: int = 0) -> None:
    tcod.map_compute_fov(fov_map, x, y, radius, light_walls, algorithm)

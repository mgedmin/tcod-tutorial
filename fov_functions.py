import tcod
import tcod.map

from game_map import GameMap


def initialize_fov(game_map: GameMap) -> tcod.map.Map:
    # order='F' means Fortran aka column-major, i.e. indexed by [x, y]
    fov_map = tcod.map.Map(game_map.width, game_map.height, order='F')

    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.transparent[x, y] = not game_map.tiles[x][y].block_sight
            fov_map.walkable[x, y] = not game_map.tiles[x][y].blocked

    return fov_map


def recompute_fov(fov_map: tcod.map.Map, x: int, y: int, radius: int,
                  light_walls: bool = True, algorithm: int = 0) -> None:
    fov_map.compute_fov(x, y, radius, light_walls, algorithm)

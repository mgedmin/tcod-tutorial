import enum
from operator import attrgetter
from typing import TYPE_CHECKING, Dict, List

import tcod

from game_messages import MessageLog
from game_states import GameStates
from game_types import cast_to_color
from menus import character_screen, inventory_menu, level_up_menu

if TYPE_CHECKING:
    from game_map import GameMap
    from entity import Entity


class RenderOrder(enum.Enum):
    STAIRS = enum.auto()
    CORPSE = enum.auto()
    ITEM = enum.auto()
    ACTOR = enum.auto()


def get_names_under_mouse(mouse: tcod.Mouse, entities: List['Entity'],
                          fov_map: tcod.map.Map) -> str:
    (x, y) = (mouse.cx, mouse.cy)

    names = [
        entity.name
        for entity in entities
        if (x, y) == (entity.x, entity.y) and tcod.map_is_in_fov(fov_map, x, y)
    ]
    return ', '.join(names).capitalize()


def render_bar(panel: tcod.console.Console, x: int, y: int, total_width: int,
               name: str, value: int, maximum: int, bar_color: tcod.Color,
               back_color: tcod.Color) -> None:
    bar_width = value * total_width // maximum

    tcod.console_set_default_background(panel, cast_to_color(back_color))
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, cast_to_color(bar_color))
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, cast_to_color(tcod.white))
    tcod.console_print_ex(panel, x + total_width // 2, y, tcod.BKGND_NONE,
                          tcod.CENTER, f"{name}: {value}/{maximum}")


def render_all(
    root_console: tcod.console.Console, con: tcod.console.Console,
    panel: tcod.console.Console, entities: List['Entity'], player: 'Entity',
    game_map: 'GameMap', fov_map: tcod.map.Map, fov_recompute: bool,
    message_log: MessageLog, screen_width: int, screen_height: int,
    bar_width: int, panel_height: int, panel_y: int, mouse: tcod.Mouse,
    colors: Dict[str, tcod.Color], game_state: GameStates,
) -> None:
    # Draw all the tiles in the game map
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight
                if visible:
                    if wall:
                        color = colors['light_wall']
                    else:
                        color = colors['light_ground']
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        color = colors['dark_wall']
                    else:
                        color = colors['dark_ground']
                else:
                    continue
                tcod.console_set_char_background(
                    con, x, y, cast_to_color(color), tcod.BKGND_SET)

    # Draw all entities in the list
    for entity in sorted(entities, key=attrgetter('render_order.value')):
        draw_entity(con, entity, fov_map, game_map)

    tcod.console_blit(con, 0, 0, screen_width, screen_height,
                      root_console, 0, 0)

    tcod.console_set_default_background(panel, cast_to_color(tcod.black))
    tcod.console_clear(panel)

    # Print the game messages, one line at a time
    for y, message in enumerate(message_log.messages, 1):
        tcod.console_set_default_foreground(
            panel, cast_to_color(message.color))
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE,
                              tcod.LEFT, message.text)

    render_bar(panel, 1, 1, bar_width,
               'HP', player.fighter.hp, player.fighter.max_hp,
               tcod.light_red, tcod.darker_red)

    render_bar(panel, 1, 2, bar_width,
               'XP', player.level.current_xp,
               player.level.experience_to_next_level,
               tcod.light_blue, tcod.darker_blue)

    tcod.console_print_ex(panel, 1, 3, tcod.BKGND_NONE, tcod.LEFT,
                          f'Player level: {player.level.current_level}')

    tcod.console_print_ex(panel, 1, 4, tcod.BKGND_NONE, tcod.LEFT,
                          f'Dungeon level: {game_map.dungeon_level}')

    tcod.console_set_default_foreground(panel, cast_to_color(tcod.light_gray))
    tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT,
                          get_names_under_mouse(mouse, entities, fov_map))

    tcod.console_blit(panel, 0, 0, screen_width, panel_height,
                      root_console, 0, panel_y)

    if game_state == GameStates.SHOW_INVENTORY:
        inventory_menu(
            root_console,
            "Press the key next to an item to use it, or Esc to cancel.\n",
            player, 50, screen_width, screen_height,
        )
    elif game_state == GameStates.DROP_INVENTORY:
        inventory_menu(
            root_console,
            "Press the key next to an item to drop it, or Esc to cancel.\n",
            player, 50, screen_width, screen_height,
        )
    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(root_console, 'Level up! Choose a stat to raise:',
                      player, 40, screen_width, screen_height)
    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(root_console, player, 30, 10,
                         screen_width, screen_height)


def clear_all(con: tcod.console.Console, entities: List['Entity']) -> None:
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con: tcod.console.Console, entity: 'Entity',
                fov_map: tcod.map.Map, game_map: 'GameMap') -> None:
    if (tcod.map_is_in_fov(fov_map, entity.x, entity.y) or
            entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        tcod.console_set_default_foreground(con, cast_to_color(entity.color))
        tcod.console_put_char(
            con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con: tcod.console.Console, entity: 'Entity') -> None:
    """Erase the character that represents this object."""
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)

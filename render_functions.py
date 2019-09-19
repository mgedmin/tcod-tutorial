import enum
import math
from operator import attrgetter
from typing import TYPE_CHECKING, Dict, List

import tcod
import tcod.event

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


def get_names_under_mouse(mouse: tcod.event.Point, entities: List['Entity'],
                          fov_map: tcod.map.Map) -> str:
    (x, y) = (mouse.x, mouse.y)

    names = [
        entity.name
        for entity in entities
        if (x, y) == (entity.x, entity.y) and fov_map.fov[x, y]
    ]
    return ', '.join(names).capitalize()


def render_bar(panel: tcod.console.Console, x: int, y: int, total_width: int,
               name: str, value: int, maximum: int, bar_color: tcod.Color,
               back_color: tcod.Color) -> None:
    bar_width = value * total_width // maximum

    panel.draw_rect(x, y, total_width, 1, ch=0, bg=cast_to_color(back_color),
                    bg_blend=tcod.BKGND_SCREEN)

    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, ch=0, bg=cast_to_color(bar_color),
                        bg_blend=tcod.BKGND_SCREEN)

    panel.print(x + total_width // 2, y, f"{name}: {value}/{maximum}",
                fg=cast_to_color(tcod.white),
                bg_blend=tcod.BKGND_NONE,
                alignment=tcod.CENTER)


def render_all(
    root_console: tcod.console.Console, con: tcod.console.Console,
    panel: tcod.console.Console, entities: List['Entity'], player: 'Entity',
    game_map: 'GameMap', fov_map: tcod.map.Map, fov_recompute: bool,
    message_log: MessageLog, screen_width: int, screen_height: int,
    bar_width: int, panel_height: int, panel_y: int, mouse: tcod.event.Point,
    colors: Dict[str, tcod.Color], game_state: GameStates,
    target_radius: int = 0,
) -> None:
    # Draw all the tiles in the game map
    for y in range(game_map.height):
        for x in range(game_map.width):
            visible = fov_map.fov[x, y]
            wall = game_map.tiles[x][y].block_sight
            if visible:
                if wall:
                    color = colors['light_wall']
                else:
                    if (game_state == GameStates.TARGETING and
                            math.hypot(x - mouse.x,
                                       y - mouse.y) <= target_radius):
                        color = colors['target_ground']
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
            con.bg[x, y] = cast_to_color(color)

    # Draw all entities in the list
    for entity in sorted(entities, key=attrgetter('render_order.value')):
        draw_entity(con, entity, fov_map, game_map)

    con.blit(root_console, 0, 0, 0, 0, screen_width, screen_height)

    panel.clear(bg=cast_to_color(tcod.black))

    # Print the game messages, one line at a time
    for y, message in enumerate(message_log.messages, 1):
        panel.print(message_log.x, y, message.text,
                    fg=cast_to_color(message.color),
                    bg_blend=tcod.BKGND_NONE,
                    alignment=tcod.LEFT)

    panel.print(1, 0, get_names_under_mouse(mouse, entities, fov_map),
                fg=cast_to_color(tcod.light_gray),
                bg_blend=tcod.BKGND_NONE,
                alignment=tcod.LEFT)

    render_bar(panel, 1, 1, bar_width,
               'HP', player.fighter.hp, player.fighter.max_hp,
               tcod.light_red, tcod.darker_red)

    render_bar(panel, 1, 2, bar_width,
               'XP', player.level.current_xp,
               player.level.experience_to_next_level,
               tcod.light_blue, tcod.darker_blue)

    panel.print(1, 3, f'Player level: {player.level.current_level}',
                fg=cast_to_color(tcod.white),
                bg_blend=tcod.BKGND_NONE,
                alignment=tcod.LEFT)
    panel.print(1, 4, f'Dungeon level: {game_map.dungeon_level}',
                fg=cast_to_color(tcod.white),
                bg_blend=tcod.BKGND_NONE,
                alignment=tcod.LEFT)

    panel.blit(root_console, 0, panel_y, 0, 0, screen_width, panel_height)

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
    if (fov_map.fov[entity.x, entity.y] or
            entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        con.ch[entity.x, entity.y] = ord(entity.char)
        con.fg[entity.x, entity.y] = cast_to_color(entity.color)


def clear_entity(con: tcod.console.Console, entity: 'Entity') -> None:
    """Erase the character that represents this object."""
    con.ch[entity.x, entity.y] = ord(' ')

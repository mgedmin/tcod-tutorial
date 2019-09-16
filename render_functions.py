import enum
from operator import attrgetter

import tcod

from game_states import GameStates
from menus import character_screen, inventory_menu, level_up_menu


class RenderOrder(enum.Enum):
    STAIRS = enum.auto()
    CORPSE = enum.auto()
    ITEM = enum.auto()
    ACTOR = enum.auto()


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [
        entity.name
        for entity in entities
        if (x, y) == (entity.x, entity.y) and tcod.map_is_in_fov(fov_map, x, y)
    ]
    return ', '.join(names).capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum,
               bar_color, back_color):
    bar_width = value * total_width // maximum

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, x + total_width // 2, y, tcod.BKGND_NONE,
                          tcod.CENTER, f"{name}: {value}/{maximum}")


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute,
               message_log, screen_width, screen_height, bar_width,
               panel_height, panel_y, mouse, colors, game_state):
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
                    con, x, y, color, tcod.BKGND_SET)

    # Draw all entities in the list
    for entity in sorted(entities, key=attrgetter('render_order.value')):
        draw_entity(con, entity, fov_map, game_map)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    # Print the game messages, one line at a time
    for y, message in enumerate(message_log.messages, 1):
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE,
                              tcod.LEFT, message.text)

    render_bar(panel, 1, 1, bar_width,
               'HP', player.fighter.hp, player.fighter.max_hp,
               tcod.light_red, tcod.darker_red)

    tcod.console_print_ex(panel, 1, 3, tcod.BKGND_NONE, tcod.LEFT,
                          f'Dungeon level: {game_map.dungeon_level}')

    tcod.console_set_default_foreground(panel, tcod.light_gray)
    tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT,
                          get_names_under_mouse(mouse, entities, fov_map))

    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state == GameStates.SHOW_INVENTORY:
        inventory_menu(
            con,
            "Press the key next to an item to use it, or Esc to cancel.\n",
            player.inventory, 50, screen_width, screen_height,
        )
    elif game_state == GameStates.DROP_INVENTORY:
        inventory_menu(
            con,
            "Press the key next to an item to drop it, or Esc to cancel.\n",
            player.inventory, 50, screen_width, screen_height,
        )
    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40,
                      screen_width, screen_height)
    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map, game_map):
    if (tcod.map_is_in_fov(fov_map, entity.x, entity.y) or
            entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(
            con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity):
    """Erase the character that represents this object."""
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)

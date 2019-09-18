from typing import Any, Dict

import tcod

from game_states import GameStates
from game_types import UserAction


def handle_keys(key: tcod.Key, game_state: GameStates,
                mouse: tcod.Mouse) -> UserAction:
    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key, mouse)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)

    return {}


def handle_player_turn_keys(key: tcod.Key) -> UserAction:
    # Movement keys
    key_char = chr(key.c)

    if key.vk == tcod.KEY_UP or key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == tcod.KEY_DOWN or key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == tcod.KEY_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT or key_char == 'l':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key_char == 'b':
        return {'move': (-1, 1)}
    elif key_char == 'n':
        return {'move': (1, 1)}

    if key_char == 'z' or key_char == '.' or key_char == ' ':
        return {'wait': True}

    if key_char == 'g':
        return {'pickup': True}

    if key_char == 'i':
        return {'show_inventory': True}

    if key_char == 'd':
        return {'drop_inventory': True}

    if key_char == 'c':
        return {'show_character_screen': True}

    if key.text == '>' or key.vk == tcod.KEY_ENTER:
        return {'take_stairs': True}

    if key.vk == tcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}


def handle_targeting_keys(key: tcod.Key, mouse: tcod.Mouse) -> UserAction:
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    if key.vk == tcod.KEY_ENTER:
        return {'left_click': (mouse.cx, mouse.cy)}

    return {}


def handle_player_dead_keys(key: tcod.Key) -> UserAction:
    key_char = chr(key.c)

    if key_char == 'i':
        return {'show_inventory': True}

    if key_char == 'c':
        return {'show_character_screen': True}

    if key.vk == tcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    return {}


def handle_inventory_keys(key: tcod.Key) -> UserAction:
    if ord('a') <= key.c <= ord('z'):
        return {'inventory_index': key.c - ord('a')}

    if key.vk == tcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}


def handle_level_up_menu(key: tcod.Key) -> UserAction:
    key_char = chr(key.c)

    if key_char == 'a':
        return {'level_up': 'hp'}
    elif key_char == 'b':
        return {'level_up': 'str'}
    elif key_char == 'c':
        return {'level_up': 'def'}

    return {}


def handle_character_screen(key: tcod.Key) -> UserAction:
    key_char = chr(key.c)

    if key_char == 'c' or key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_main_menu(key: tcod.Key) -> UserAction:
    key_char = chr(key.c)
    if key_char == 'a':
        return {'new_game': True}
    if key_char == 'b':
        return {'load_game': True}
    if key_char == 'c' or key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    return {}


def handle_mouse(mouse: tcod.Mouse) -> UserAction:
    x, y = mouse.cx, mouse.cy

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    return {}

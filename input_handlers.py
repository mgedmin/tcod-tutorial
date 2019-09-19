import tcod
import tcod.event

from game_states import GameStates
from game_types import UserAction


def handle_keys(event: tcod.event.KeyboardEvent, game_state: GameStates,
                mouse: tcod.event.Point) -> UserAction:
    if event.sym == tcod.event.K_RETURN and event.mod & tcod.event.KMOD_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(event)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(event)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(event, mouse)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(event)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(event)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(event)

    return {}


def handle_player_turn_keys(event: tcod.event.KeyboardEvent) -> UserAction:
    # Movement keys
    if event.sym in (tcod.event.K_UP, tcod.event.K_k):
        return {'move': (0, -1)}
    elif event.sym in (tcod.event.K_DOWN, tcod.event.K_j):
        return {'move': (0, 1)}
    elif event.sym in (tcod.event.K_LEFT, tcod.event.K_h):
        return {'move': (-1, 0)}
    elif event.sym in (tcod.event.K_RIGHT, tcod.event.K_l):
        return {'move': (1, 0)}
    elif event.sym == tcod.event.K_y:
        return {'move': (-1, -1)}
    elif event.sym == tcod.event.K_u:
        return {'move': (1, -1)}
    elif event.sym == tcod.event.K_b:
        return {'move': (-1, 1)}
    elif event.sym == tcod.event.K_n:
        return {'move': (1, 1)}

    if event.sym in (tcod.event.K_z, tcod.event.K_PERIOD, tcod.event.K_SPACE):
        return {'wait': True}

    if event.sym == tcod.event.K_g:
        return {'pickup': True}

    if event.sym == tcod.event.K_i:
        return {'show_inventory': True}

    if event.sym == tcod.event.K_d:
        return {'drop_inventory': True}

    if event.sym == tcod.event.K_c:
        return {'show_character_screen': True}

    if event.sym in (tcod.event.K_GREATER, tcod.event.K_RETURN):
        # XXX: K_GREATER is not what I thought it was!
        return {'take_stairs': True}

    if event.sym == tcod.event.K_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}


def handle_targeting_keys(event: tcod.event.KeyboardEvent,
                          mouse: tcod.event.Point) -> UserAction:
    if event.sym == tcod.event.K_ESCAPE:
        return {'exit': True}

    if event.sym == tcod.event.K_RETURN:
        return {'left_click': (mouse.x, mouse.y)}

    return {}


def handle_player_dead_keys(event: tcod.event.KeyboardEvent) -> UserAction:
    if event.sym == tcod.event.K_i:
        return {'show_inventory': True}

    if event.sym == tcod.event.K_c:
        return {'show_character_screen': True}

    if event.sym == tcod.event.K_ESCAPE:
        # Exit the game
        return {'exit': True}

    return {}


def handle_inventory_keys(event: tcod.event.KeyboardEvent) -> UserAction:
    if tcod.event.K_a <= event.sym <= tcod.event.K_z:
        return {'inventory_index': event.sym - tcod.event.K_a}

    if event.sym == tcod.event.K_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}


def handle_level_up_menu(event: tcod.event.KeyboardEvent) -> UserAction:
    if event.sym == tcod.event.K_a:
        return {'level_up': 'hp'}
    elif event.sym == tcod.event.K_b:
        return {'level_up': 'str'}
    elif event.sym == tcod.event.K_c:
        return {'level_up': 'def'}

    return {}


def handle_character_screen(event: tcod.event.KeyboardEvent) -> UserAction:
    if event.sym in (tcod.event.K_c, tcod.event.K_ESCAPE):
        return {'exit': True}

    return {}


def handle_main_menu(event: tcod.event.KeyboardEvent) -> UserAction:
    if event.sym == tcod.event.K_a:
        return {'new_game': True}
    if event.sym == tcod.event.K_b:
        return {'load_game': True}
    if event.sym in (tcod.event.K_c, tcod.event.K_ESCAPE):
        return {'exit': True}

    if event.sym == tcod.event.K_RETURN and event.mod & tcod.event.KMOD_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    return {}


def handle_mouse(event: tcod.event.MouseButtonEvent) -> UserAction:
    x, y = event.tile.x, event.tile.y

    if event.button == tcod.event.BUTTON_LEFT:
        return {'left_click': (x, y)}
    elif event.button == tcod.event.BUTTON_RIGHT:
        return {'right_click': (x, y)}

    return {}

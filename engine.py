#!/usr/bin/python3
import sys
from typing import Dict, List, Optional

import tcod
import tcod.console

from data_loaders import load_game, save_game
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_map import GameMap
from game_messages import Message, MessageLog
from game_states import GameStates
from game_types import UserAction
from initialize_new_game import constants, get_game_variables
from input_handlers import handle_keys, handle_main_menu, handle_mouse
from menus import main_menu, message_box
from render_functions import clear_all, render_all


def main() -> None:
    tcod.console_set_custom_font(
        'arial10x10.png',
        tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD,
    )
    with tcod.console_init_root(
        constants.screen_width, constants.screen_height,
        constants.window_title,
        fullscreen=False,
        vsync=True,
        renderer=tcod.RENDERER_SDL2,
    ) as root_console:
        tcod.sys_set_fps(60)

        main_menu_loop(root_console)


def main_menu_loop(root_console: tcod.console.Console) -> None:
    con = tcod.console.Console(
        constants.screen_width, constants.screen_height, order='F')
    panel = tcod.console.Console(
        constants.screen_width, constants.panel_height, order='F')

    player = None
    entities: List[Entity] = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = tcod.image_load('menu_background1.png')

    while True:
        action: UserAction = {}
        # We pass a 1 second timeout to wait() primarily to give a chance for
        # the Python interpreter to react to ^C in a relatively timely manner.
        for event in tcod.event.wait(1):
            if event.type == 'QUIT':
                sys.exit()
            elif event.type == 'KEYDOWN':
                action = handle_main_menu(event)
            if action:
                break

        if show_main_menu:
            main_menu(root_console, main_menu_background_image,
                      constants.screen_width, constants.screen_height)

            if show_load_error_message:
                message_box(root_console, 'No save game to load', 50,
                            constants.screen_width, constants.screen_height)

            tcod.console_flush()

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')
            fullscreen = action.get('fullscreen')

            if fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            if show_load_error_message and (
                    new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                (player, entities, game_map,
                 message_log, game_state) = get_game_variables()
                show_main_menu = False
            elif load_saved_game:
                try:
                    (player, entities, game_map,
                     message_log, game_state) = load_game()
                except FileNotFoundError:
                    show_load_error_message = True
                else:
                    show_main_menu = False
            elif exit_game:
                break

        else:
            con.clear()
            assert player is not None
            assert game_map is not None
            assert message_log is not None
            assert game_state is not None
            play_game(player, entities, game_map, message_log, game_state,
                      root_console, con, panel)
            show_main_menu = True


def play_game(player: Entity, entities: List[Entity], game_map: GameMap,
              message_log: MessageLog, game_state: GameStates,
              root_console: tcod.console.Console, con: tcod.console.Console,
              panel: tcod.console.Console) -> None:
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    mouse = tcod.event.Point(-1, -1)

    if player.fighter.hp > 0:
        game_state = GameStates.PLAYERS_TURN
    else:
        game_state = GameStates.PLAYER_DEAD
    previous_game_state = game_state

    targeting_item = None

    while True:
        action: UserAction = {}
        for event in tcod.event.wait(1):
            if event.type == 'QUIT':
                # XXX: what happens if I do this when in the character screen?
                # or inventory? or while targeting?  will the game load fine?
                save_game(player, entities, game_map, message_log, game_state)
                sys.exit()
            elif event.type == 'KEYDOWN':
                action = handle_keys(event, game_state, mouse)
            elif event.type == 'MOUSEMOTION':
                mouse = event.tile
            elif event.type == 'MOUSEBUTTONDOWN':
                mouse = event.tile
                action = handle_mouse(event)
            if action:
                break

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants.fov_radius,
                          constants.fov_light_walls, constants.fov_algorithm)

        target_radius = 0
        if targeting_item and targeting_item.item:
            target_radius = targeting_item.item.function_kwargs.get('radius',
                                                                    0)

        render_all(
            root_console,
            con, panel, entities, player, game_map, fov_map, fov_recompute,
            message_log, constants.screen_width, constants.screen_height,
            constants.bar_width, constants.panel_height, constants.panel_y,
            mouse, constants.colors, game_state, target_radius,
        )

        fov_recompute = False

        tcod.console_flush()

        clear_all(con, entities)

        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        show_character_screen = action.get('show_character_screen')
        take_stairs = action.get('take_stairs')
        level_up = action.get('level_up')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = action.get('left_click')
        right_click = action.get('right_click')

        player_turn_results: List[Dict] = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            new_x = player.x + dx
            new_y = player.y + dy
            if not game_map.is_blocked(new_x, new_y):
                target = get_blocking_entities_at_location(
                    entities, new_x, new_y)
                if target:
                    player_turn_results.extend(player.fighter.attack(target))
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        if wait and game_state == GameStates.PLAYERS_TURN:
            game_state = GameStates.ENEMY_TURN

        if pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if (entity.x == player.x and entity.y == player.y and
                        entity.item):
                    player_turn_results.extend(
                        player.inventory.add_item(entity))
                    break
            else:
                message_log.add_message(
                    Message('There is nothing here to pick up.', tcod.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if (inventory_index is not None
                and previous_game_state != GameStates.PLAYER_DEAD
                and inventory_index < len(player.inventory.items)):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(
                    player.inventory.use(item, entities=entities,
                                         fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if take_stairs and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if (entity.stairs and
                        entity.x == player.x and entity.y == player.y):
                    save_game(player, entities, game_map, message_log,
                              game_state)
                    entities = game_map.next_floor(player, message_log,
                                                   constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    con.clear()
                    break
            else:
                message_log.add_message(
                    Message('There are no stairs here.', tcod.yellow))

        if level_up:
            if level_up == 'hp':
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == 'str':
                player.fighter.base_power += 1
            elif level_up == 'def':
                player.fighter.base_defense += 1
            game_state = previous_game_state

        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click
                player_turn_results.extend(
                    player.inventory.use(
                        targeting_item, entities=entities, fov_map=fov_map,
                        target_x=target_x, target_y=target_y))
            elif right_click:
                player_turn_results.append({
                    'targeting_cancelled': True,
                })

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY,
                              GameStates.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({
                    'targeting_cancelled': True,
                })
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added: Optional[Entity] = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(
                    targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)
                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')
                    if equipped:
                        message_log.add_message(Message(
                            f"You equipped the {equipped.name}."
                        ))
                    if dequipped:
                        message_log.add_message(Message(
                            f"You removed the {dequipped.name}."
                        ))
                game_state = GameStates.ENEMY_TURN

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(
                    Message(f'You gain {xp} experience points.'))
                if leveled_up:
                    message_log.add_message(Message(
                        f'Your battle skills grow stronger!'
                        f' You reached level {player.level.current_level}!',
                        tcod.yellow))
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(
                        player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == "__main__":
    main()

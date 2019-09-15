#!/usr/bin/python3
import tcod

from death_functions import kill_player, kill_monster
from entity import Entity, get_blocking_entities_at_location
from fighter import Fighter
from fov_functions import initialize_fov, recompute_fov
from game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates
from input_handlers import handle_keys
from render_functions import render_all, clear_all, RenderOrder


def main():
    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50),
    }

    player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True,
                    render_order=RenderOrder.ACTOR,
                    fighter=Fighter(hp=30, defense=2, power=5))
    entities = [player]

    tcod.console_set_custom_font(
        'arial10x10.png',
        tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD,
    )
    tcod.console_init_root(
        screen_width, screen_height,
        'tcod tutorial revised',
        fullscreen=False,
    )

    con = tcod.console_new(screen_width, screen_height)
    panel = tcod.console_new(screen_width, panel_height)

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, player,
                      entities, max_monsters_per_room)

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    message_log = MessageLog(message_x, message_width, message_height)

    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameStates.PLAYERS_TURN

    while not tcod.console_is_window_closed():
        # XXX: how do I get key autorepeating?
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
                                 key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius,
                          fov_light_walls, fov_algorithm)

        render_all(
            con, panel, entities, player, game_map, fov_map, fov_recompute,
            message_log, screen_width, screen_height, bar_width,
            panel_height, panel_y, mouse, colors)

        fov_recompute = False

        tcod.console_flush()

        clear_all(con, entities)

        key = tcod.console_check_for_keypress()
        action = handle_keys(key)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        player_turn_results = []

        # XXX: I don't like how this means we might be dropping key events!
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

        if exit:
            return

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

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

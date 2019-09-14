#!/usr/bin/python3
import tcod

from entity import Entity
from game_map import GameMap
from input_handlers import handle_keys
from render_functions import render_all, clear_all


def main():
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
    }

    player = Entity(screen_width // 2, screen_height // 2, '@', tcod.white)
    npc = Entity(screen_width // 2 - 5, screen_height // 2, '@', tcod.yellow)
    entities = [npc, player]

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

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, player)

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        render_all(
            con, entities, game_map, screen_width, screen_height, colors)

        tcod.console_flush()

        clear_all(con, entities)

        key = tcod.console_check_for_keypress()
        action = handle_keys(key)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if exit:
            return


if __name__ == "__main__":
    main()

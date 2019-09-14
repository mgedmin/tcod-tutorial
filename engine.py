#!/usr/bin/python3
import tcod


def main():
    screen_width = 80
    screen_height = 50

    player_x = screen_width // 2
    player_y = screen_height // 2

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

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        tcod.console_set_default_foreground(con, tcod.white)
        tcod.console_put_char(con, player_x, player_y, '@', tcod.BKGND_NONE)
        tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
        tcod.console_flush()

        tcod.console_put_char(con, player_x, player_y, ' ', tcod.BKGND_NONE)

        key = tcod.console_check_for_keypress()
        action = handle_keys(key)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            player_x += dx
            player_y += dy

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if exit:
            return


def handle_keys(key):
    # Movement keys
    if key.vk == tcod.KEY_UP:
        return {'move': (0, -1)}
    elif key.vk == tcod.KEY_DOWN:
        return {'move': (0, 1)}
    elif key.vk == tcod.KEY_LEFT:
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT:
        return {'move': (1, 0)}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}


if __name__ == "__main__":
    main()

import tcod


def render_all(con, entities, game_map, screen_width, screen_height, colors):
    # Draw all the tiles in the game map
    for y in range(game_map.height):
        for x in range(game_map.width):
            wall = game_map.tiles[x][y].block_sight
            if wall:
                color = colors['dark_wall']
            else:
                color = colors['dark_ground']
            tcod.console_set_char_background(con, x, y, color, tcod.BKGND_SET)
    # Draw all entities in the list
    for entity in entities:
        draw_entity(con, entity)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity):
    tcod.console_set_default_foreground(con, entity.color)
    tcod.console_put_char(
        con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity):
    """Erase the character that represents this object."""
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)

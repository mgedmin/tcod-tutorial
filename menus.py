from typing import TYPE_CHECKING, List

import tcod
import tcod.console

from game_types import cast_to_color

if TYPE_CHECKING:
    from entity import Entity


def menu(root_console: tcod.console.Console, header: str, options: List[str],
         width: int, screen_width: int, screen_height: int) -> None:
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per
    # option
    header_height = root_console.get_height_rect(
        0, 0, width, screen_height, header)
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = tcod.console.Console(width, height, order='F')

    # print the header, with auto-wrap
    window.print_box(0, 0, width, height, header,
                     fg=cast_to_color(tcod.white),
                     bg_blend=tcod.BKGND_NONE,
                     alignment=tcod.LEFT)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = f'({chr(letter_index)}) {option_text}'
        window.print(0, y, text, fg=cast_to_color(tcod.white),
                     bg_blend=tcod.BKGND_NONE, alignment=tcod.LEFT)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.blit(root_console, x, y, 0, 0, width, height, 1.0, 0.7)


def inventory_menu(
    root_console: tcod.console.Console, header: str, player: 'Entity',
    inventory_width: int, screen_width: int, screen_height: int,
) -> None:
    # show a menu with each item of the inventory as an option
    if not player.inventory.items:
        # XXX: I don't like this getting an option letter like '(a)'
        options = ['Inventory is empty.']
    else:
        options = []
        for item in player.inventory.items:
            if player.equipment.is_equipped(item):
                slot = player.equipment.where_equipped(item)
                options.append(f"{item.name} (on {slot.value})")
            else:
                options.append(item.name)

    menu(root_console, header, options, inventory_width,
         screen_width, screen_height)


def level_up_menu(
    root_console: tcod.console.Console, header: str, player: 'Entity',
    menu_width: int, screen_width: int, screen_height: int,
) -> None:
    options = [
        f'Constitution (+20 HP, from {player.fighter.max_hp})',
        f'Strength (+1 attack, from {player.fighter.power})',
        f'Agility (+1 defense, from {player.fighter.defense})',
    ]
    menu(root_console, header, options, menu_width,
         screen_width, screen_height)


def character_screen(
    root_console: tcod.console.Console, player: 'Entity',
    character_screen_width: int, character_screen_height: int,
    screen_width: int, screen_height: int,
) -> None:
    window = tcod.console.Console(
        character_screen_width, character_screen_height, order='F')

    text = [
        'Character Information',
        f'Level: {player.level.current_level}',
        f'Experience: {player.level.current_xp}',
        f'Experience to Level: {player.level.experience_to_next_level}',
        f'Maximum HP: {player.fighter.max_hp}',
        f'Attack: {player.fighter.power}',
        f'Defense: {player.fighter.defense}',
    ]

    for y, line in enumerate(text, 1):
        window.print_box(
            0, y, character_screen_width, character_screen_height,
            line, fg=cast_to_color(tcod.white), bg_blend=tcod.BKGND_NONE,
            alignment=tcod.LEFT)

    x = (screen_width - character_screen_width) // 2
    y = (screen_height - character_screen_height) // 2
    window.blit(root_console, x, y, 0, 0,
                character_screen_width, character_screen_height,
                1.0, 0.7)


def main_menu(root_console: tcod.console.Console,
              background_image: tcod.image.Image,
              screen_width: int, screen_height: int) -> None:
    background_image.blit_2x(root_console, 0, 0)

    root_console.print(screen_width // 2, screen_height // 2 - 4,
                       "TOMBS OF THE ANCIENT KINGS",
                       fg=cast_to_color(tcod.light_yellow),
                       bg_blend=tcod.BKGND_NONE,
                       alignment=tcod.CENTER)
    root_console.print(screen_width // 2, screen_height - 2,
                       "By Marius Gedminas (but not really)",
                       fg=cast_to_color(tcod.light_yellow),
                       bg_blend=tcod.BKGND_NONE,
                       alignment=tcod.CENTER)
    menu(root_console, '', ['Play a new game', 'Continue last game', 'Quit'],
         24, screen_width, screen_height)


def message_box(root_console: tcod.console.Console, header: str, width: int,
                screen_width: int, screen_height: int) -> None:
    menu(root_console, header, [], width, screen_width, screen_height)

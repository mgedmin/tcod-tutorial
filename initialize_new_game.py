from typing import List, Tuple

import tcod

from entity import Entity
from equipment import Equipment
from equipment_slots import EquipmentSlots
from equippable import Equippable
from fighter import Fighter
from game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates
from inventory import Inventory
from level import Level
from render_functions import RenderOrder


class constants:
    window_title = "Roguelike Tutorial Revised"

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

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50),
        'target_ground': tcod.Color(200, 40, 20),
    }


def get_game_variables() -> Tuple[Entity, List[Entity], GameMap, MessageLog,
                                  GameStates]:
    player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True,
                    render_order=RenderOrder.ACTOR,
                    fighter=Fighter(hp=100, defense=1, power=2),
                    inventory=Inventory(26),
                    equipment=Equipment(),
                    level=Level())
    entities = [player]

    dagger = Entity(0, 0, '-', tcod.sky, 'Dagger',
                    render_order=RenderOrder.ITEM,
                    equippable=Equippable(
                        EquipmentSlots.MAIN_HAND,
                        power_bonus=2))
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    game_map = GameMap(constants.map_width, constants.map_height)
    game_map.make_map(
        constants.max_rooms, constants.room_min_size, constants.room_max_size,
        player, entities)

    message_log = MessageLog(
        constants.message_x, constants.message_width, constants.message_height)

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state

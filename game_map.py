import random
from typing import TYPE_CHECKING, List, Type

import tcod

from ai import BasicMonster
from entity import Entity
from equipment_slots import EquipmentSlots
from equippable import Equippable
from fighter import Fighter
from game_messages import Message, MessageLog
from item import Item
from item_functions import cast_confuse, cast_fireball, cast_lightning, heal
from map_objects import Tile
from random_utils import from_dungeon_level, random_choice_from_dict
from rectangle import Rect
from render_functions import RenderOrder
from stairs import Stairs

if TYPE_CHECKING:
    from initialize_new_game import constants


class GameMap:

    def __init__(self, width: int, height: int,
                 dungeon_level: int = 1) -> None:
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self) -> List[List[Tile]]:
        # Whoa there, a column-major matrix?  You don't see those every day!
        tiles = [
            [Tile(blocked=True) for y in range(self.height)]
            for x in range(self.width)
        ]

        return tiles

    def make_map(self, max_rooms: int, room_min_size: int, room_max_size: int,
                 player: Entity, entities: List[Entity]) -> None:
        rooms: List[Rect] = []

        for r in range(max_rooms):
            # random width and height
            w = random.randint(room_min_size, room_max_size)
            h = random.randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = random.randrange(self.width - w)
            y = random.randrange(self.height - h)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # make sure the room doesn't intersect with any of the others
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                new_x, new_y = new_room.center()

                if not rooms:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    prev_x, prev_y = rooms[-1].center()

                    # flip a coin
                    if random.randrange(2):
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities)

                # finally, append the new room to the list
                rooms.append(new_room)

        center_of_last_room_x, center_of_last_room_y = rooms[-1].center()
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y,
                             '>', tcod.white, 'Stairs',
                             render_order=RenderOrder.STAIRS,
                             stairs=Stairs(self.dungeon_level + 1))
        entities.append(down_stairs)

    def create_room(self, room: Rect) -> None:
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y] = Tile(blocked=False)

    def create_h_tunnel(self, x1: int, x2: int, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y] = Tile(blocked=False)

    def create_v_tunnel(self, y1: int, y2: int, x: int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = Tile(blocked=False)

    def place_entities(self, room: Rect, entities: List[Entity]) -> None:
        max_monsters_per_room = from_dungeon_level(self.dungeon_level, [
            # value, first level for this value
            (2, 1),
            (3, 4),
            (5, 6),
        ])
        max_items_per_room = from_dungeon_level(self.dungeon_level, [
            (1, 1),
            (2, 4),
        ])
        number_of_monsters = random.randint(0, max_monsters_per_room)
        number_of_items = random.randint(0, max_items_per_room)

        monster_chances = {
            'orc': 80,
            'troll': from_dungeon_level(self.dungeon_level, [
                (15, 3),
                (30, 5),
                (60, 7),
            ]),
        }
        item_chances = {
            'healing_potion': 35,
            'sword': from_dungeon_level(self.dungeon_level, [
                (5, 4),
            ]),
            'shield': from_dungeon_level(self.dungeon_level, [
                (15, 8),
            ]),
            'lightning_scroll': from_dungeon_level(self.dungeon_level, [
                (25, 4),
            ]),
            'fireball_scroll': from_dungeon_level(self.dungeon_level, [
                (25, 6),
            ]),
            'confusion_scroll': from_dungeon_level(self.dungeon_level, [
                (10, 2),
            ]),
        }

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = random.randrange(room.x1 + 1, room.x2)
            y = random.randrange(room.y1 + 1, room.y2)

            if not any(x == entity.x and y == entity.y
                       for entity in entities):
                monster_choice = random_choice_from_dict(monster_chances)
                if monster_choice == 'orc':
                    monster = Entity(
                        x, y, 'o', tcod.desaturated_green, 'Orc', blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=Fighter(hp=20, defense=0, power=4, xp=35),
                        ai=BasicMonster(),
                    )
                elif monster_choice == 'troll':
                    monster = Entity(
                        x, y, 'T', tcod.darker_green, 'Troll', blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=Fighter(hp=30, defense=2, power=8, xp=100),
                        ai=BasicMonster(),
                    )
                else:
                    assert False, f'unhandled monster_choice: {monster_choice}'
                entities.append(monster)

        for i in range(number_of_items):
            x = random.randrange(room.x1 + 1, room.x2)
            y = random.randrange(room.y1 + 1, room.y2)

            if not any(x == entity.x and y == entity.y
                       for entity in entities):
                item_choice = random_choice_from_dict(item_chances)
                if item_choice == 'healing_potion':
                    item = Entity(x, y, '!', tcod.violet, 'Healing Potion',
                                  render_order=RenderOrder.ITEM,
                                  item=Item(heal, amount=40))
                elif item_choice == 'sword':
                    item = Entity(x, y, '/', tcod.sky, 'Sword',
                                  render_order=RenderOrder.ITEM,
                                  equippable=Equippable(
                                      EquipmentSlots.MAIN_HAND,
                                      power_bonus=3))
                elif item_choice == 'shield':
                    item = Entity(x, y, '[', tcod.sky, 'Shield',
                                  render_order=RenderOrder.ITEM,
                                  equippable=Equippable(
                                      EquipmentSlots.OFF_HAND,
                                      defense_bonus=1))
                elif item_choice == 'fireball_scroll':
                    item = Entity(x, y, '#', tcod.red, 'Fireball Scroll',
                                  render_order=RenderOrder.ITEM,
                                  item=Item(cast_fireball, targeting=True,
                                            targeting_message=Message(
                                                'Left-click a target tile'
                                                ' for the fireball, or'
                                                ' right-click to cancel.',
                                                tcod.light_cyan,
                                            ),
                                            damage=25, radius=3))
                elif item_choice == 'confusion_scroll':
                    item = Entity(x, y, '#', tcod.light_pink,
                                  'Confusion Scroll',
                                  render_order=RenderOrder.ITEM,
                                  item=Item(cast_confuse, targeting=True,
                                            targeting_message=Message(
                                                'Left-click an enemy'
                                                ' to confuse it, or'
                                                ' right-click to cancel.',
                                                tcod.light_cyan,
                                            )))
                elif item_choice == 'lightning_scroll':
                    item = Entity(x, y, '#', tcod.yellow, 'Lightning Scroll',
                                  render_order=RenderOrder.ITEM,
                                  item=Item(cast_lightning,
                                            damage=40, maximum_range=5))
                else:
                    assert False, f'unhandled item_choice: {item_choice}'
                entities.append(item)

    def is_blocked(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y].blocked
        else:
            return True

    def next_floor(self, player: Entity,
                   message_log: MessageLog,
                   constants: Type['constants']) -> List[Entity]:
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(
            constants.max_rooms, constants.room_min_size,
            constants.room_max_size, player, entities)

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(
            Message('You take a moment to rest, and recover your strength.',
                    tcod.light_violet))

        return entities

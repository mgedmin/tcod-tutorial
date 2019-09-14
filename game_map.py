import random

import tcod

from map_objects import Tile
from rectangle import Rect
from entity import Entity


class GameMap:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        # Whoa there, a column-major matrix?  You don't see those every day!
        tiles = [
            [Tile(blocked=True) for y in range(self.height)]
            for x in range(self.width)
        ]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, player,
                 entities, max_monsters_per_room):
        rooms = []

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

                self.place_entities(new_room, entities, max_monsters_per_room)

                # finally, append the new room to the list
                rooms.append(new_room)

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y] = Tile(blocked=False)

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y] = Tile(blocked=False)

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = Tile(blocked=False)

    def place_entities(self, room, entities, max_monsters_per_room):
        # Get a random number of monsters
        number_of_monsters = random.randint(0, max_monsters_per_room)

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = random.randrange(room.x1 + 1, room.x2)
            y = random.randrange(room.y1 + 1, room.y2)

            if not any(x == entity.x and y == entity.y
                       for entity in entities):
                if random.randrange(100) < 80:
                    monster = Entity(x, y, 'o', tcod.desaturated_green,
                                     'Orc', blocks=True)
                else:
                    monster = Entity(x, y, 'T', tcod.darker_green,
                                     'Troll', blocks=True)
                entities.append(monster)

    def is_blocked(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y].blocked
        else:
            return True
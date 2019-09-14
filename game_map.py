from map_objects import Tile


class GameMap:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        # Whoa there, a column-major matrix?  You don't see those every day!
        tiles = [
            [Tile(blocked=False) for y in range(self.height)]
            for x in range(self.width)
        ]

        tiles[30][22] = Tile(blocked=True)
        tiles[31][22] = Tile(blocked=True)
        tiles[32][22] = Tile(blocked=True)

        return tiles

    def is_blocked(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y].blocked
        else:
            return True

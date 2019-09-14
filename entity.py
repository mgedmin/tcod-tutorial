class Entity:
    """A generic object to represent players, enemies, items etc."""

    def __init__(self, x, y, char, color, name, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks

    def move(self, dx, dy):
        """Move the entity by a given amount."""
        self.x += dx
        self.y += dy


def get_blocking_entities_at_location(entities, x, y):
    for entity in entities:
        if entity.blocks and entity.x == x and entity.y == y:
            return entity

    return None

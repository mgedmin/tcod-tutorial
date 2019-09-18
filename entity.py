import math
from typing import List, Optional, TYPE_CHECKING

import tcod

from components import component
from item import Item
from render_functions import RenderOrder

if TYPE_CHECKING:  # noqa: F401
    from game_map import GameMap
    from ai import AIComponent
    from equipment import Equipment
    from equippable import Equippable
    from fighter import Fighter
    from inventory import Inventory
    from level import Level
    from stairs import Stairs


class Entity:
    """A generic object to represent players, enemies, items etc."""

    fighter = component('fighter')
    ai = component('ai')
    item = component('item')
    inventory = component('inventory')
    stairs = component('stairs')
    level = component('level')
    equipment = component('equipment')
    equippable = component('equippable')

    def __init__(self, x: int, y: int, char: str, color: tcod.Color, name: str,
                 blocks: bool = False,
                 render_order: RenderOrder = RenderOrder.CORPSE,
                 fighter: Optional['Fighter'] = None,
                 ai: Optional['AIComponent'] = None,
                 item: Optional['Item'] = None,
                 inventory: Optional['Inventory'] = None,
                 stairs: Optional['Stairs'] = None,
                 level: Optional['Level'] = None,
                 equipment: Optional['Equipment'] = None,
                 equippable: Optional['Equippable'] = None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order

        # Components
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable

        if self.equippable and not self.item:
            self.item = Item()

    def move(self, dx: int, dy: int) -> None:
        """Move the entity by a given amount."""
        self.x += dx
        self.y += dy

    def move_towards(self, target_x: int, target_y: int, game_map: 'GameMap',
                     entities: List['Entity']) -> None:
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        if (not game_map.is_blocked(self.x + dx, self.y + dy) and
                not get_blocking_entities_at_location(
                    entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_astar(self, target: 'Entity', entities: List['Entity'],
                   game_map: 'GameMap') -> None:
        # Create a FOV map that has the dimensions of the map
        fov = tcod.map.Map(game_map.width, game_map.height, order='F')

        # Scan the current map each turn and set all the walls as unwalkable
        for y in range(game_map.height):
            for x in range(game_map.width):
                fov.transparent[x, y] = not game_map.tiles[x][y].block_sight
                fov.walkable[x, y] = not game_map.tiles[x][y].blocked

        # Scan all the objects to see if there are objects that must be
        # navigated around
        # Check also that the object isn't self or the target (so that the
        # start and the end points are free)
        # The AI class handles the situation if self is next to the target so
        # it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                fov.walkable[entity.x, entity.y] = False

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0
        # if diagonal moves are prohibited
        my_path = tcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's
        # coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter
        # than 25 tiles
        # The path size matters if you want the monster to use alternative
        # longer paths (for example through other rooms) if for example the
        # player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters
        # from running around the map if there's an alternative path really far
        # away
        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            next_x, next_y = tcod.path_walk(my_path, True)
            if next_x is not None and next_y is not None:
                # Set self's coordinates to the next path tile
                self.x = next_x
                self.y = next_y
        else:
            # Keep the old move function as a backup so that if there are no
            # paths (for example another monster blocks a corridor) it will
            # still try to move towards the player (closer to the corridor
            # opening)
            self.move_towards(target.x, target.y, game_map, entities)

        # Delete the path to free memory
        tcod.path_delete(my_path)

    def distance(self, x: int, y: int) -> float:
        return math.hypot(self.x - x, self.y - y)

    def distance_to(self, other: 'Entity') -> float:
        dx = other.x - self.x
        dy = other.y - self.y
        return math.hypot(dx, dy)


def get_blocking_entities_at_location(entities: List[Entity],
                                      x: int, y: int) -> Optional[Entity]:
    for entity in entities:
        if entity.blocks and entity.x == x and entity.y == y:
            return entity

    return None

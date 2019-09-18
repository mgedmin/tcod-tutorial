import random
from typing import TYPE_CHECKING, List

import tcod

from components import Component
from game_messages import Message
from game_types import ActionResults

if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap


class AIComponent(Component):

    def take_turn(
        self, target: 'Entity', fov_map: tcod.map.Map,
        game_map: 'GameMap', entities: List['Entity'],
    ) -> ActionResults:
        raise NotImplementedError


class BasicMonster(AIComponent):

    def take_turn(
        self, target: 'Entity', fov_map: tcod.map.Map,
        game_map: 'GameMap', entities: List['Entity'],
    ) -> ActionResults:
        results: ActionResults = []

        monster = self.owner
        if fov_map.fov[monster.x, monster.y]:
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.hp > 0:
                results.extend(monster.fighter.attack(target))

        return results


class ConfusedMonster(AIComponent):

    def __init__(self, previous_ai: AIComponent,
                 number_of_turns: int = 10) -> None:
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(
        self, target: 'Entity', fov_map: tcod.map.Map,
        game_map: 'GameMap', entities: List['Entity'],
    ) -> ActionResults:
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + random.randint(-1, 1)
            random_y = self.owner.y + random.randint(-1, 1)

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({
                'message': Message(
                    f"The {self.owner.name} is no longer confused!"
                ),
            })

        return results

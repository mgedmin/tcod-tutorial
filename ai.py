import random

import tcod

from game_messages import Message


class BasicMonster:

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        if tcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.hp > 0:
                results.extend(monster.fighter.attack(target))

        return results


class ConfusedMonster:

    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
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

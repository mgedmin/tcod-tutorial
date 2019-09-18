import random
from typing import Dict, List, Tuple, TypeVar

T = TypeVar('T')


def from_dungeon_level(dungeon_level: int,
                       table: List[Tuple[int, int]]) -> int:
    for value, level in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


def random_choice_index(chances: List[int]) -> int:
    random_chance = random.randrange(sum(chances))

    for choice, w in enumerate(chances):
        if random_chance <= w:
            return choice
        random_chance -= w

    assert False


def random_choice_from_dict(choice_dict: Dict[T, int]) -> T:
    choices = list(choice_dict)
    chances = list(choice_dict.values())
    return choices[random_choice_index(chances)]

import random


def from_dungeon_level(dungeon_level, table):
    for value, level in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


def random_choice_index(chances):
    random_chance = random.randrange(sum(chances))

    for choice, w in enumerate(chances):
        if random_chance <= w:
            return choice
        random_chance -= w


def random_choice_from_dict(choice_dict):
    choices = list(choice_dict)
    chances = list(choice_dict.values())
    return choices[random_choice_index(chances)]

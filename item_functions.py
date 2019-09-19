from typing import Any, List

import tcod

from ai import ConfusedMonster
from entity import Entity
from game_messages import Message
from game_types import ActionResults


def heal(entity: Entity, *, amount: int, **_: Any) -> ActionResults:
    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({
            'consumed': False,
            'message': Message('You are already at full health', tcod.yellow),
        })
    else:
        entity.fighter.heal(amount)
        results.append({
            'consumed': True,
            'message': Message('Your wounds start to feel better!',
                               tcod.green),
        })

    return results


def cast_lightning(
    caster: Entity, *, entities: List[Entity], fov_map: tcod.map.Map,
    damage: int, maximum_range: float, **_: Any
) -> ActionResults:
    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if (entity.fighter and entity != caster
                and fov_map.fov[entity.x, entity.y]):
            distance = caster.distance_to(entity)
            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({
            'consumed': True,
            'target': target,
            'message': Message(
                f"A lighting bolt strikes the {target.name}"
                f" with a loud thunder! The damage is {damage}",
                tcod.orange,
            ),
        })
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({
            'consumed': False,
            'target': None,
            'message': Message(
                "No enemy is close enough to strike.", tcod.red,
            ),
        })

    return results


def cast_fireball(
    entity: Entity, *, entities: List[Entity], fov_map: tcod.map.Map,
    damage: int, radius: int, target_x: int, target_y: int, **_: Any
) -> ActionResults:
    results = []

    if not fov_map.fov[target_x, target_y]:
        results.append({
            'consumed': False,
            'message': Message(
                "You cannot target a tile outside your field of view.",
                tcod.yellow,
            )
        })
        return results

    results.append({
        'consumed': True,
        'message': Message(
            f"The fireball explodes, burning everything"
            f" within {radius} tiles!",
            tcod.orange,
        ),
    })

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({
                'message': Message(
                    f"The {entity.name} gets burned for {damage} hit points.",
                    tcod.orange,
                ),
            })
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confuse(
    entity: Entity, *, fov_map: tcod.map.Map, entities: List[Entity],
    target_x: int, target_y: int, **_: Any
) -> ActionResults:
    results = []

    if not fov_map.fov[target_x, target_y]:
        results.append({
            'consumed': False,
            'message': Message(
                "You cannot target a tile outside your field of view.",
                tcod.yellow,
            ),
        })
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, 10)
            confused_ai.owner = entity
            entity.ai = confused_ai
            results.append({
                'consumed': True,
                'message': Message(
                    f"The eyes of the {entity.name} look vacant, as he starts"
                    f" to stumble around!",
                    tcod.light_green),
            })
            break
    else:
        results.append({
            'consumed': False,
            'message': Message(
                "There is no targetable enemy at that location.",
                tcod.yellow),
        })

    return results

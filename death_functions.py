from typing import Tuple

import tcod

from entity import Entity
from game_messages import Message
from game_states import GameStates
from render_functions import RenderOrder


def kill_player(player: Entity) -> Tuple[Message, GameStates]:
    player.char = '%'
    player.color = tcod.dark_red
    return (Message('You died!', tcod.red), GameStates.PLAYER_DEAD)


def kill_monster(monster: Entity) -> Message:
    death_message = Message(f'{monster.name.capitalize()} is dead!',
                            tcod.orange)

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f'remains of {monster.name}'
    monster.render_order = RenderOrder.CORPSE
    return death_message

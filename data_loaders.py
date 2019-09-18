import os
import shelve
from typing import List, Tuple

from entity import Entity
from game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates


def save_game(player: Entity, entities: List[Entity], game_map: GameMap,
              message_log: MessageLog, game_state: GameStates) -> None:
    with shelve.open('savegame.dat', 'n') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['game_map'] = game_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state


def load_game() -> Tuple[Entity, List[Entity], GameMap, MessageLog,
                         GameStates]:
    if not os.path.isfile('savegame.dat'):
        raise FileNotFoundError

    with shelve.open('savegame.dat', 'r') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']
    player = entities[player_index]
    return player, entities, game_map, message_log, game_state

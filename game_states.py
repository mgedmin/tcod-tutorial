import enum


class GameStates(enum.Enum):
    PLAYERS_TURN = enum.auto()
    ENEMY_TURN = enum.auto()
    PLAYER_DEAD = enum.auto()
    SHOW_INVENTORY = enum.auto()
    DROP_INVENTORY = enum.auto()
    TARGETING = enum.auto()

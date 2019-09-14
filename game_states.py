import enum


class GameStates(enum.Enum):
    PLAYERS_TURN = enum.auto()
    ENEMY_TURN = enum.auto()
    PLAYER_DEAD = enum.auto()

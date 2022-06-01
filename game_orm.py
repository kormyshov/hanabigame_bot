from typing import Literal, Union, List, NamedTuple
from enum import Enum

from sequence import Sequence


Hint = Union[Literal[0], Literal[1], Literal[2], Literal[3], Literal[4], Literal[5], Literal[6], Literal[7], Literal[8]]
Live = Union[Literal[0], Literal[1], Literal[2], Literal[3]]


class GameState(Enum):
    NOT_START = 0
    WAITING_START = 1
    FINISH = 2
    TURN_PLAYER_ONE = 5
    TURN_PLAYER_TWO = 6
    TURN_PLAYER_THREE = 7
    TURN_PLAYER_FOUR = 8
    TURN_PLAYER_FIVE = 9
    TURN_PLAYER_ONE_LAST = 10
    TURN_PLAYER_TWO_LAST = 11
    TURN_PLAYER_THREE_LAST = 12
    TURN_PLAYER_FOUR_LAST = 13
    TURN_PLAYER_FIVE_LAST = 14


class GameORM(NamedTuple):
    id: str
    state: GameState
    stack: Sequence
    table: Sequence
    trash: Sequence
    hints: Hint
    lives: Live
    player_ids: List[str]

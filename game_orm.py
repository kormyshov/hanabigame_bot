from typing import Literal, Union, List, NamedTuple
from enum import IntEnum

from sequence import Sequence


Hint = Union[Literal[0], Literal[1], Literal[2], Literal[3], Literal[4], Literal[5], Literal[6], Literal[7], Literal[8]]
Live = Union[Literal[0], Literal[1], Literal[2], Literal[3]]


class GameState(IntEnum):
    NOT_START = 0
    WAITING_START = 1
    FINISH = 2
    TURN_PLAYER_ONE = 5
    TURN_PLAYER_TWO = 6
    TURN_PLAYER_THREE = 7
    TURN_PLAYER_FOUR = 8
    TURN_PLAYER_FIVE = 9
    TURN_PLAYER_ONE_LAST_ONE = 10
    TURN_PLAYER_TWO_LAST_ONE = 11
    TURN_PLAYER_THREE_LAST_ONE = 12
    TURN_PLAYER_FOUR_LAST_ONE = 13
    TURN_PLAYER_FIVE_LAST_ONE = 14
    TURN_PLAYER_ONE_LAST_TWO = 15
    TURN_PLAYER_TWO_LAST_TWO = 16
    TURN_PLAYER_THREE_LAST_TWO = 17
    TURN_PLAYER_FOUR_LAST_TWO = 18
    TURN_PLAYER_FIVE_LAST_TWO = 19
    TURN_PLAYER_ONE_LAST_THREE = 20
    TURN_PLAYER_TWO_LAST_THREE = 21
    TURN_PLAYER_THREE_LAST_THREE = 22
    TURN_PLAYER_FOUR_LAST_THREE = 23
    TURN_PLAYER_FIVE_LAST_THREE = 24
    TURN_PLAYER_ONE_LAST_FOUR = 25
    TURN_PLAYER_TWO_LAST_FOUR = 26
    TURN_PLAYER_THREE_LAST_FOUR = 27
    TURN_PLAYER_FOUR_LAST_FOUR = 28
    TURN_PLAYER_FIVE_LAST_FOUR = 29
    TURN_PLAYER_ONE_LAST_FIVE = 30
    TURN_PLAYER_TWO_LAST_FIVE = 31
    TURN_PLAYER_THREE_LAST_FIVE = 32
    TURN_PLAYER_FOUR_LAST_FIVE = 33
    TURN_PLAYER_FIVE_LAST_FIVE = 34


class GameORM(NamedTuple):
    id: str
    state: GameState
    stack: Sequence
    table: Sequence
    trash: Sequence
    hints: Hint
    lives: Live
    player_ids: List[str]

import random
from enum import Enum
from typing import Literal, Union, List, NamedTuple

import database
from player import Player
from sequence import Sequence
from card import (
    Card,
    CardColors,
    CardNumbers,
)
from exceptions import GameDoesntInit, GameStackIsEmpty, DontExistCard


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


Hint = Union[Literal[0], Literal[1], Literal[2], Literal[3], Literal[4], Literal[5], Literal[6], Literal[7], Literal[8]]
Live = Union[Literal[0], Literal[1], Literal[2], Literal[3]]


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def clear(cls):
        cls._instances.pop(cls, None)


class TableInfo(NamedTuple):
    table: Sequence
    hints: Hint
    lives: Live


class ConnectionResult(Enum):
    OK = 1
    OK_AND_START = 2


class ConnectionResponse(NamedTuple):
    result: ConnectionResult
    players: List[Player]


def init_list() -> List[Card]:
    lst: List[Card] = []
    for color in CardColors:
        if color == CardColors.RAINBOW:
            continue
        for count in range(3):
            lst.append(Card(CardNumbers.ONE, color))
        for number in (CardNumbers.TWO, CardNumbers.THREE, CardNumbers.FOUR):
            for count in range(2):
                lst.append(Card(number, color))
        lst.append(Card(CardNumbers.FIVE, color))

    for number in CardNumbers:
        lst.append(Card(number, CardColors.RAINBOW))

    return lst


class Game(metaclass=Singleton):
    def __init__(self, game_id: str):
        self.id: str = game_id
        self.loaded: bool = False
        self.state: GameState = GameState.NOT_START
        self.stack: Sequence = Sequence()
        self.table: Sequence = Sequence()
        self.trash: Sequence = Sequence()
        self.hints: Hint = 0
        self.lives: Live = 0
        self.players: List[Player] = []

    def load(self):
        if not self.loaded:
            pass
    #         response = database.get_game_info(self.id)
    #         if 'Item' in response:
    #             self.state = response['Item']['state']
    #             self.stack = Sequence.from_str(response['Item'].get('stack', None))
    #             self.table = Sequence.from_str(response['Item'].get('table', None))
    #             self.trash = Sequence.from_str(response['Item'].get('trash', None))
    #
    #             for i in range(1, 6):
    #                 player_id = response['Item'].get('player' + str(i), None)
    #                 if player_id is not None:
    #                     self.players.append(player.Player(player_id))
    #
    #             self.hints = response['Item'].get('hints', 0)
    #             self.lives = response['Item'].get('lives', 0)
    #
    #         self.loaded = True
    #
    # def save(self):
    #     player_to_id = {('player' + str(k + 1), player.id) for k, player in enumerate(self.players)}
    #     stack = self.stack.to_str() if self.stack is not None else ''
    #     table = self.table.to_str() if self.table is not None else ''
    #     trash = self.trash.to_str() if self.trash is not None else ''
    #     database.set_game_info(self.id, self.state, stack, table, trash, player_to_id, self.hints, self.lives)

    def get_table_info(self) -> TableInfo:
        return TableInfo(self.table, self.hints, self.lives)

    def get_trash_cards(self) -> Sequence:
        return self.trash

    def init_game(self, player: Player) -> None:
        self.state = GameState.WAITING_START
        self.connect_player(player)

    def finish(self) -> None:
        for player in self.players:
            player.finish()

        database.finish_game(self.id)

    def connect_player(self, player: Player) -> ConnectionResponse:
        if self.state != GameState.WAITING_START:
            raise GameDoesntInit

        self.players.append(player)
        player.connect_to_game(self)

        return ConnectionResponse(
            ConnectionResult.OK if len(self.players) < 5 else ConnectionResult.OK_AND_START,
            self.players,
        )

    def start(self) -> None:
        lst = init_list()
        random.shuffle(lst)
        cnt = 5 if len(self.players) < 4 else 4

        for i, p in enumerate(self.players):
            p.start_game(Sequence(lst[i * cnt:(i + 1) * cnt]))

        self.stack = Sequence(lst[cnt * len(self.players):])
        self.state = GameState.TURN_PLAYER_ONE

        self.hints = 8
        self.lives = 3

    def take_card(self) -> Card:
        try:
            return self.stack.pop()
        except IndexError:
            self.state += 5
            raise GameStackIsEmpty

    def add_to_trash(self, card: Card) -> None:
        self.trash.append(card)

    def add_to_table(self, card: Card) -> bool:
        try:
            previous_card = card.get_previous_card()
            if previous_card not in self.table:
                self.add_to_trash(card)
                self.lives -= 1
                return False
            index = self.table.index(previous_card)
            self.table.pop(index)
        except DontExistCard:
            pass
        self.table.append(card)

        try:
            card.get_next_card()
        except DontExistCard:
            self.hints = min(self.hints + 1, 8)
        return True

    def hint_color(self, recipient_number: int, color: CardColors) -> List[int]:
        recipient = self.players[recipient_number]
        card_numbers = recipient.get_card_numbers_with_color(color)
        self.hints -= 1
        return card_numbers

    def hint_value(self, recipient_number: int, value: CardNumbers) -> List[int]:
        recipient = self.players[recipient_number]
        card_numbers = recipient.get_card_numbers_with_value(value)
        self.hints -= 1
        return card_numbers

    def next_turn(self) -> int:
        self.state += 1
        if self.state - len(self.players) == GameState.TURN_PLAYER_ONE:
            self.state = GameState.TURN_PLAYER_ONE
        return self.state - GameState.TURN_PLAYER_ONE

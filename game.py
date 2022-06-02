import logging
import random
import hashlib
from enum import Enum
from typing import List, NamedTuple

import database
from player import Player
from sequence import Sequence
from card import (
    Card,
    CardColors,
    CardNumbers,
)
from exceptions import (
    GameDoesntInit,
    GameStackIsEmpty,
    DontExistCard,
    GameDoesntExistInDB,
)
from game_orm import (
    Hint,
    Live,
    GameState,
    GameORM,
)


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
    def __init__(self, game_id: str) -> None:
        self.id: str = game_id
        self.loaded: bool = False
        self.state: GameState = GameState.NOT_START
        self.stack: Sequence = Sequence()
        self.table: Sequence = Sequence()
        self.trash: Sequence = Sequence()
        self.hints: Hint = 0
        self.lives: Live = 0
        self.players: List[Player] = []

    def load(self) -> None:
        if not self.loaded:
            try:
                response: GameORM = database.get_game_info(self.id)
                self.state = response.state
                self.stack = response.stack
                self.table = response.table
                self.trash = response.trash
                self.hints = response.hints
                self.lives = response.lives
                self.players = [Player(player_id) for player_id in response.player_ids]
            except GameDoesntExistInDB:
                pass

            self.loaded = True

    def save(self):
        database.set_game_info(GameORM(
            id=self.id,
            state=self.state,
            stack=self.stack,
            table=self.table,
            trash=self.trash,
            hints=self.hints,
            lives=self.lives,
            player_ids=[player.id for player in self.players],
        ))

    def get_table_info(self) -> TableInfo:
        return TableInfo(self.table, self.hints, self.lives)

    def get_trash_cards(self) -> Sequence:
        return self.trash

    def init_game(self, player: Player) -> str:
        logger = logging.getLogger('hanabigame.game.init_game')
        logger.info('start')
        self.id = hashlib.md5(str(int(player.id) + random.randint(-1000000, 1000000)).encode('utf-8')).hexdigest()
        self.state = GameState.WAITING_START
        logger.info('set state WAITING_START')
        self.connect_player(player)
        logger.info('connected first player')
        return self.id

    def finish(self) -> None:
        logger = logging.getLogger('hanabigame.game.finish')
        logger.info('start')
        for player in self.players:
            database.clear_player(player.id)
        logger.info('players finished')

        database.clear_game(self.id)
        logger.info('game finished')

    def connect_player(self, player: Player) -> ConnectionResponse:
        logger = logging.getLogger('hanabigame.game.connect_player')
        logger.info('start')
        if self.state != GameState.WAITING_START:
            raise GameDoesntInit

        self.players.append(player)
        logger.info('player append to list')
        player.connect_to_game(self.id)
        logger.info('player connected')

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

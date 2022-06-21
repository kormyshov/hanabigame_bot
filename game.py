import logging
import random
import hashlib
from enum import Enum
from typing import List, NamedTuple, Optional, Tuple

from abstract_base import AbstractBase, GameDoesntExistInDB
from player import Player
from sequence import Sequence
from card import (
    Card,
    CardColors,
    CardNumbers,
    DontExistCard,
)
from game_orm import (
    Hint,
    Live,
    GameState,
    GameORM,
)


class DatabaseIsNone(Exception):
    pass


class GameStackIsEmpty(Exception):
    pass


class GameDoesntInit(Exception):
    pass


class GameIsEnded(Exception):
    pass


class TableInfo(NamedTuple):
    table: Sequence
    hints: Hint
    lives: Live


class ConnectionResult(Enum):
    OK = 1
    OK_AND_START = 2


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


class Game:
    def __init__(self) -> None:
        self.id: Optional[str] = None
        self.database: Optional[AbstractBase] = None
        self.loaded: bool = False
        self.state: GameState = GameState.NOT_START
        self.stack: Sequence = Sequence()
        self.table: Sequence = Sequence()
        self.trash: Sequence = Sequence()
        self.hints: Hint = 0
        self.lives: Live = 0
        self.players: List[Player] = []

    def __str__(self) -> str:
        return 'Game(id: {}, state: {}, hints: {}, lives: {}, table: {}, trash: {}, stack: {}, player_ids: {})'.format(
            self.id,
            str(self.state),
            str(self.hints),
            str(self.lives),
            str(self.table),
            str(self.trash),
            str(self.stack),
            ' '.join(map(lambda o: o.id, self.players)),
        )

    def load(self) -> None:
        if not self.loaded:
            if self.database is None:
                raise DatabaseIsNone
            try:
                response: GameORM = self.database.get_game_info(self.id)
                self.state = response.state
                self.stack = response.stack
                self.table = response.table
                self.trash = response.trash
                self.hints = response.hints
                self.lives = response.lives
                self.players = [Player(player_id, self.database) for player_id in response.player_ids]
            except GameDoesntExistInDB:
                pass

            self.loaded = True

    def save(self):
        if self.database is None:
            raise DatabaseIsNone
        self.database.set_game_info(GameORM(
            id=self.id,
            state=self.state,
            stack=self.stack,
            table=self.table,
            trash=self.trash,
            hints=self.hints,
            lives=self.lives,
            player_ids=[player.id for player in self.players],
        ))

    def set_id(self, game_id: str) -> None:
        self.id = game_id

    def set_database(self, database: AbstractBase) -> None:
        self.database = database

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
        if self.database is None:
            logger.info('database is None')
            raise DatabaseIsNone
        for player in self.players:
            self.database.clear_player(player.id)
        logger.info('players finished')

        self.database.clear_game(self.id)
        logger.info('game finished')

    def connect_player(self, player: Player) -> ConnectionResult:
        logger = logging.getLogger('hanabigame.game.connect_player')
        logger.info('start')
        if self.state != GameState.WAITING_START:
            raise GameDoesntInit

        self.players.append(player)
        logger.info('player append to list')
        player.connect_to_game(self.id)
        logger.info('player connected')

        return ConnectionResult.OK if len(self.players) < 5 else ConnectionResult.OK_AND_START

    def start(self) -> None:
        lst = init_list()
        random.shuffle(lst)
        cnt = 5 if len(self.players) < 4 else 4

        for i, p in enumerate(self.players):
            p.start_game(Sequence(lst[i * cnt:(i + 1) * cnt]))
            p.save()

        self.stack = Sequence(lst[cnt * len(self.players):])
        self.state = GameState.TURN_PLAYER_ONE

        self.hints = 8
        self.lives = 3

    def take_card(self) -> Card:
        try:
            return self.stack.pop()
        except IndexError:
            self.state += 5 * (self.state - 4)
            raise GameStackIsEmpty

    def move_card_to_player(self, player: Player) -> None:
        try:
            card = self.take_card()
            player.put_card(card)
        except GameStackIsEmpty:
            pass

    def move_to_trash(self, player: Player, card_number: int) -> Card:
        trashed_card = player.get_card(card_number)
        self.trash.append(trashed_card)
        self.hints = min(self.hints + 1, 8)
        self.move_card_to_player(player)
        player.set_playing_state()
        return trashed_card

    def move_to_table(self, player: Player, card_number: int) -> Tuple[bool, Card]:
        put_card = player.get_card(card_number)
        success = True
        if self.add_to_table(put_card):
            try:
                put_card.get_next_card()
            except DontExistCard:
                self.hints = min(self.hints + 1, 8)
        else:
            self.trash.append(put_card)
            self.lives -= 1
            success = False
            if self.lives == 0:
                pass  # TODO: сделать обработку конца игры
        self.move_card_to_player(player)
        player.set_playing_state()
        return success, put_card

    def add_to_table(self, card: Card) -> bool:
        try:
            previous_card = card.get_previous_card()
            if previous_card not in self.table:
                return False
            index = self.table.index(previous_card)
            self.table.pop(index)
        except DontExistCard:
            if len(self.table.get_card_numbers(lambda c: c.color == card.color)) > 0:
                return False
        self.table.append(card)
        return True

    def hint_color(self, player: Player, recipient_number: int, color_str: str) -> List[int]:
        recipient = self.players[recipient_number]
        color = next(filter(lambda c: c.value == color_str or c.value == CardColors.RAINBOW.value, CardColors))
        card_numbers = recipient.get_card_numbers_with_color(color)
        self.hints -= 1
        player.set_playing_state()
        return card_numbers

    def hint_value(self, player: Player, recipient_number: int, value_str: str) -> List[int]:
        recipient = self.players[recipient_number]
        value = next(filter(lambda c: c.value == int(value_str), CardNumbers))
        card_numbers = recipient.get_card_numbers_with_value(value)
        self.hints -= 1
        player.set_playing_state()
        return card_numbers

    def next_turn(self) -> int:
        if 35 <= self.state <= 39:
            raise GameIsEnded
        self.state += 1
        if 10 <= self.state <= 34 and self.state // 5 - 2 == self.state % 5:
            self.state = GameState.LAST_TURN_ONE + self.state % 5
        if (self.state - len(self.players)) % 5 == 0:
            self.state -= self.state % 5
        return int(self.state % 5)

    def is_player_turn(self, player: Player) -> bool:
        return self.players[int(self.state - GameState.TURN_PLAYER_ONE) % 5].id == player.id

    def get_score(self):
        score = 0
        for n in CardNumbers:
            score += n.value * len(self.table.get_card_numbers(lambda c: c.number == n))
        return score

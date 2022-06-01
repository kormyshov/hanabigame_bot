from enum import Enum
from typing import Optional, NamedTuple, List
import random
import hashlib
import logging

import database
import game
from sequence import Sequence
from exceptions import PlayerDoesntExistInDB, UnexpectedPlayerState
from card import Card, CardColors, CardNumbers


class PlayerState(Enum):
    NOT_PLAYING = 0
    PLAYING = 1
    CONFIRM_FINISH_WAITING_GAME = 2
    WAITING_START_GAME = 3
    CONFIRM_FINISH_STARTED_GAME = 4
    REQUEST_GAME_CODE_TO_CONNECT = 5
    REQUEST_MOVE_TO_TRASH = 6
    REQUEST_MOVE_TO_TABLE = 7
    REQUEST_HINT_RECIPIENT = 8
    REQUEST_HINT_TYPE_ONE = 9
    REQUEST_HINT_TYPE_TWO = 10
    REQUEST_HINT_TYPE_THREE = 11
    REQUEST_HINT_TYPE_FOUR = 12
    REQUEST_HINT_TYPE_FIVE = 13
    REQUEST_HINT_ONE_COLOR = 14
    REQUEST_HINT_TWO_COLOR = 15
    REQUEST_HINT_THREE_COLOR = 16
    REQUEST_HINT_FOUR_COLOR = 17
    REQUEST_HINT_FIVE_COLOR = 18
    REQUEST_HINT_ONE_VALUE = 19
    REQUEST_HINT_TWO_VALUE = 20
    REQUEST_HINT_THREE_VALUE = 21
    REQUEST_HINT_FOUR_VALUE = 22
    REQUEST_HINT_FIVE_VALUE = 23


class PlayerORM(NamedTuple):
    id: str
    name: Optional[str]
    state: PlayerState
    game_id: Optional[str]
    hand: Sequence


class Player:
    def __init__(self, chat_id: str) -> None:
        self.id: str = chat_id
        self.loaded: bool = False
        self.state: PlayerState = PlayerState.NOT_PLAYING
        self.hand: Sequence = Sequence()
        self.game_id: Optional[str] = None
        self.name: Optional[str] = None

    def load(self) -> None:
        if not self.loaded:
            try:
                response: PlayerORM = database.get_player_info(self.id)
                self.name = response.name
                self.state = response.state
                self.game_id = response.game_id
                self.hand = response.hand
            except PlayerDoesntExistInDB:
                pass

            self.loaded = True

    def save(self) -> None:
        database.set_player_info(PlayerORM(
            id=self.id,
            name=self.name,
            state=self.state,
            game_id=self.game_id,
            hand=self.hand,
        ))

    def get_name(self) -> str:
        self.load()
        return self.name

    def set_name(self, name: str) -> None:
        if self.get_name() != name:
            self.name = name
            self.save()

    def get_game_id(self) -> Optional[str]:
        self.load()
        return self.game_id

    def get_hand_cards(self) -> Sequence:
        self.load()
        return self.hand

    def confirm_finish_game(self) -> None:
        self.load()
        if self.state == PlayerState.PLAYING:
            self.state = PlayerState.CONFIRM_FINISH_STARTED_GAME
        elif self.state == PlayerState.WAITING_START_GAME:
            self.state = PlayerState.CONFIRM_FINISH_WAITING_GAME
        else:
            raise UnexpectedPlayerState
        self.save()

    def reject_finish_game(self) -> None:
        self.load()
        if self.state == PlayerState.CONFIRM_FINISH_STARTED_GAME:
            self.state = PlayerState.PLAYING
        elif self.state == PlayerState.CONFIRM_FINISH_WAITING_GAME:
            self.state = PlayerState.WAITING_START_GAME
        else:
            raise UnexpectedPlayerState
        self.save()

    def request_move_to_trash(self) -> int:
        self.load()
        self.state = PlayerState.REQUEST_MOVE_TO_TRASH
        self.save()
        return self.hand.len()

    def request_move_to_table(self) -> int:
        self.load()
        self.state = PlayerState.REQUEST_MOVE_TO_TABLE
        self.save()
        return self.hand.len()

    def request_hint_recipient(self) -> None:
        self.load()
        self.state = PlayerState.REQUEST_HINT_RECIPIENT
        self.save()

    def request_hint_type(self, recipient_number: int) -> None:
        self.load()
        self.state = PlayerState.REQUEST_HINT_TYPE_ONE + recipient_number
        self.save()

    def request_hint_color(self) -> None:
        self.load()
        self.state = PlayerState.REQUEST_HINT_ONE_COLOR + (self.state - PlayerState.REQUEST_HINT_TYPE_ONE)
        self.save()

    def request_hint_value(self) -> None:
        self.load()
        self.state = PlayerState.REQUEST_HINT_ONE_VALUE + (self.state - PlayerState.REQUEST_HINT_TYPE_ONE)
        self.save()

    # def create_new_game(self):
    #     game_id = hashlib.md5(str(int(self.id) + random.randint(-1000000, 1000000)).encode('utf-8')).hexdigest()
    #     self.game = game.Game(game_id)
    #     self.game.to_waiting_start(self)
    #     self.state = PlayerState.WAITING_START_GAME
    #     self.save()
    #
    #     return game_id

    def request_game_code_to_connect(self) -> None:
        self.load()
        self.state = PlayerState.REQUEST_GAME_CODE_TO_CONNECT
        self.save()

    def is_request_game_code_to_connect(self) -> bool:
        self.load()
        return self.state == PlayerState.REQUEST_GAME_CODE_TO_CONNECT

    def connect_to_game(self, game_id: str) -> None:
        self.game_id = game_id
        self.state = PlayerState.WAITING_START_GAME
        self.save()

    def move_to_trash(self, card_number: int) -> Card:
        self.load()
        trashed_card = self.hand.pop(card_number)
        self.game.add_to_trash(trashed_card)
        new_card = self.game.take_card()
        self.hand.append(new_card)
        self.save()
        return trashed_card

    def move_to_table(self, card_number: int) -> Card:
        self.load()
        put_card = self.hand.pop(card_number)
        success = self.game.add_to_table(put_card)
        new_card = self.game.take_card()
        self.hand.append(new_card)
        self.save()
        return put_card, success

    def is_request_card_number_to_trash(self) -> bool:
        self.load()
        return self.state == PlayerState.REQUEST_MOVE_TO_TRASH

    def is_request_card_number_to_put(self) -> bool:
        self.load()
        return self.state == PlayerState.REQUEST_MOVE_TO_TABLE

    def is_request_hint_recipient(self) -> bool:
        self.load()
        return self.state == PlayerState.REQUEST_HINT_RECIPIENT

    def is_request_hint_type(self) -> bool:
        self.load()
        return PlayerState.REQUEST_HINT_TYPE_ONE <= self.state <= PlayerState.REQUEST_HINT_TYPE_FIVE

    def is_request_hint_color(self) -> bool:
        self.load()
        return PlayerState.REQUEST_HINT_ONE_COLOR <= self.state <= PlayerState.REQUEST_HINT_FIVE_COLOR

    def is_request_hint_value(self) -> bool:
        self.load()
        return PlayerState.REQUEST_HINT_ONE_VALUE <= self.state <= PlayerState.REQUEST_HINT_FIVE_VALUE

    def get_recipient_hint_number(self) -> int:
        self.load()
        if PlayerState.REQUEST_HINT_ONE_COLOR <= self.state <= PlayerState.REQUEST_HINT_FIVE_COLOR:
            return int(self.state - PlayerState.REQUEST_HINT_ONE_COLOR)
        return int(self.state - PlayerState.REQUEST_HINT_ONE_VALUE)

    def get_card_numbers_with_color(self, color: CardColors) -> List[int]:
        self.load()
        card_numbers = self.hand.get_card_numbers(lambda c: c.color == color)
        return card_numbers

    def get_card_numbers_with_value(self, value: CardNumbers) -> List[int]:
        self.load()
        card_numbers = self.hand.get_card_numbers(lambda c: c.number == value)
        return card_numbers

    def start_game(self, hand: Sequence) -> None:
        self.load()
        self.state = PlayerState.PLAYING
        self.hand = hand
        self.save()

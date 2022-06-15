from typing import Optional, List

import logging
from abstract_base import AbstractBase, PlayerDoesntExistInDB
from sequence import Sequence
from card import Card, CardColors, CardNumbers
from player_orm import PlayerState, PlayerORM


class UnexpectedPlayerState(Exception):
    pass


class Player:
    def __init__(self, chat_id: str, database: AbstractBase) -> None:
        self.id: str = chat_id
        self.database: AbstractBase = database
        self.loaded: bool = False
        self.state: PlayerState = PlayerState.NOT_PLAYING
        self.hand: Sequence = Sequence()
        self.game_id: Optional[str] = None
        self.name: Optional[str] = None

    def __str__(self) -> str:
        return 'Player(id: {}, name: {}, state: {}, game_id: {}, hand: {})'.format(
            self.id,
            self.name,
            str(self.state.name),
            self.game_id,
            str(self.hand),
        )

    def load(self) -> None:
        logger = logging.getLogger('hanabigame.player.load')
        logger.info('start')
        if not self.loaded:
            logger.info('not loaded id = ' + self.id)
            try:
                response: PlayerORM = self.database.get_player_info(self.id)
                logger.info('get PlayerORM')
                self.name = response.name
                self.state = response.state
                self.game_id = response.game_id
                self.hand = response.hand
            except PlayerDoesntExistInDB:
                logger.info('player doesnt exist in db')

            self.loaded = True
        logger.info('loaded id = ' + self.id)

    def save(self) -> None:
        logger = logging.getLogger('hanabigame.player.save')
        logger.info('start')
        self.database.set_player_info(PlayerORM(
            id=self.id,
            name=self.name,
            state=self.state,
            game_id=self.game_id,
            hand=self.hand,
        ))

    def get_name(self) -> str:
        logger = logging.getLogger('hanabigame.player.get_name')
        logger.info('start')
        self.load()
        logger.info('loaded')
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    def is_not_playing(self) -> bool:
        self.load()
        return self.state == PlayerState.NOT_PLAYING

    def is_playing(self) -> bool:
        self.load()
        return self.state == PlayerState.PLAYING

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

    def reject_connect_to_game(self) -> None:
        self.load()
        self.state = PlayerState.NOT_PLAYING

    def reject_finish_game(self) -> None:
        self.load()
        if self.state == PlayerState.CONFIRM_FINISH_STARTED_GAME:
            self.state = PlayerState.PLAYING
        elif self.state == PlayerState.CONFIRM_FINISH_WAITING_GAME:
            self.state = PlayerState.WAITING_START_GAME
        else:
            raise UnexpectedPlayerState

    def request_move_to_trash(self) -> int:
        self.load()
        self.state = PlayerState.REQUEST_MOVE_TO_TRASH
        return self.hand.len()

    def request_move_to_table(self) -> int:
        self.load()
        self.state = PlayerState.REQUEST_MOVE_TO_TABLE
        return self.hand.len()

    def request_hint_recipient(self) -> None:
        self.load()
        self.state = PlayerState.REQUEST_HINT_RECIPIENT

    def request_hint_type(self, recipient_number: int) -> None:
        self.load()
        self.state = PlayerState.REQUEST_HINT_TYPE_ONE + recipient_number

    def request_hint_color(self) -> None:
        self.load()
        self.state = PlayerState.REQUEST_HINT_ONE_COLOR + (self.state - PlayerState.REQUEST_HINT_TYPE_ONE)

    def request_hint_value(self) -> None:
        self.load()
        self.state = PlayerState.REQUEST_HINT_ONE_VALUE + (self.state - PlayerState.REQUEST_HINT_TYPE_ONE)

    def request_game_code_to_connect(self) -> None:
        self.load()
        self.state = PlayerState.REQUEST_GAME_CODE_TO_CONNECT

    def is_request_game_code_to_connect(self) -> bool:
        self.load()
        return self.state == PlayerState.REQUEST_GAME_CODE_TO_CONNECT

    def connect_to_game(self, game_id: str) -> None:
        logger = logging.getLogger('hanabigame.player.connect_to_game')
        logger.info('start')
        self.game_id = game_id
        logger.info('set game_id')
        self.state = PlayerState.WAITING_START_GAME
        logger.info('set state')

    def get_card(self, card_number: int) -> Card:
        logger = logging.getLogger('hanabigame.player.get_card')
        logger.info('start')
        self.load()
        logger.info('loaded')
        card = self.hand.pop(card_number)
        logger.info('get card ' + str(card) + 'other: ' + str(self.hand))
        return card

    def put_card(self, card: Card) -> None:
        logger = logging.getLogger('hanabigame.player.put_card')
        logger.info('start with card ' + str(card))
        self.load()
        logger.info('loaded with hand: ' + str(self.hand))
        self.hand.append(card)
        logger.info('appended hand = ' + str(self.hand))

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

    def end_turn(self) -> None:
        self.load()
        self.state = PlayerState.PLAYING

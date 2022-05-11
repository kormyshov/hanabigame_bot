import os
import random
import hashlib
import logging

import database
import game
from sequence import Sequence, num_to_card


class PlayerState:
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


class Player:

    def __init__(self, chat_id):
        self.id = str(chat_id)
        self.loaded = False

        self.name = None
        self.state = PlayerState.NOT_PLAYING
        self.game = None
        self.hand = None

    def load(self):
        logger = logging.getLogger('hanabigame.player.load')
        logger.info('start')
        if not self.loaded:
            logger.info('process...')
            response = database.get_player_info(self.id)
            logger.info('get response')

            if 'Item' in response:
                logger.info('Iten in response')
                self.name = response['Item'].get('name', self.name)
                logger.info('get name')
                self.state = response['Item'].get('state', PlayerState.NOT_PLAYING)
                logger.info('get state')
                game_id = response['Item'].get('game_id', None)
                logger.info('get game_id ' + str(game_id))
                if game_id is not None:
                    self.game = game.Game(game_id)
                    logger.info('get Game')

                self.hand = Sequence.from_str(response['Item'].get('hand', None))
                logger.info('get hand')

            self.loaded = True

    def save(self):
        print('into save')
        game_id = self.game.id if self.game is not None else None
        hand = self.hand.to_str() if self.hand is not None else ''
        database.set_player_info(self.id, self.name, self.state, game_id, hand)
        print('out from save')

    def get_name(self):
        logger = logging.getLogger('hanabigame.player.get_name')
        logger.info('start')
        self.load()
        logger.info('loaded')
        return self.name

    def set_name(self, name):
        self.name = name

    def get_game(self):
        logger = logging.getLogger('hanabigame.player.get_game')
        logger.info('start')
        self.load()
        logger.info('load')
        return self.game

    def get_hand_output(self):
        self.load()
        return self.hand.to_output() if self.hand is not None else ''

    def finish(self):
        database.finish_game_for_player(self.id)

    def confirm_finish_game(self):
        self.load()
        self.state = PlayerState.CONFIRM_FINISH_STARTED_GAME if self.state == PlayerState.PLAYING else PlayerState.CONFIRM_FINISH_WAITING_GAME
        self.save()

    def request_move_to_trash(self):
        logger = logging.getLogger('hanabigame.player.request_move_to_trash')
        logger.info('start')
        self.load()
        logger.info('loaded')
        self.state = PlayerState.REQUEST_MOVE_TO_TRASH
        logger.info('set new state')
        self.save()
        logger.info('saved')
        return self.hand.len()

    def request_move_to_table(self):
        logger = logging.getLogger('hanabigame.player.request_move_to_table')
        logger.info('start')
        self.load()
        logger.info('loaded')
        self.state = PlayerState.REQUEST_MOVE_TO_TABLE
        logger.info('set new state')
        self.save()
        logger.info('saved')
        return self.hand.len()

    def request_hint_recipient(self):
        logger = logging.getLogger('hanabigame.player.request_hint_recipient')
        logger.info('start')
        self.load()
        logger.info('loaded')
        self.state = PlayerState.REQUEST_HINT_RECIPIENT
        logger.info('set new state')
        self.save()
        logger.info('saved')

    def request_hint_type(self, recipient_number):
        logger = logging.getLogger('hanabigame.player.request_hint_type')
        logger.info('start')
        self.load()
        logger.info('loaded')
        self.state = PlayerState.REQUEST_HINT_TYPE_ONE + recipient_number
        logger.info('set new state')
        self.save()
        logger.info('saved')

    def request_hint_color(self):
        logger = logging.getLogger('hanabigame.player.request_hint_color')
        logger.info('start')
        self.load()
        logger.info('loaded')
        self.state = PlayerState.REQUEST_HINT_ONE_COLOR + (self.state - PlayerState.REQUEST_HINT_TYPE_ONE)
        logger.info('set new state')
        self.save()
        logger.info('saved')

    def request_hint_value(self):
        logger = logging.getLogger('hanabigame.player.request_hint_value')
        logger.info('start')
        self.load()
        logger.info('loaded')
        self.state = PlayerState.REQUEST_HINT_ONE_VALUE + (self.state - PlayerState.REQUEST_HINT_TYPE_ONE)
        logger.info('set new state')
        self.save()
        logger.info('saved')

    def reject_finish_game(self):
        self.load()
        self.state = PlayerState.PLAYING if self.state == PlayerState.CONFIRM_FINISH_STARTED_GAME else PlayerState.WAITING_START_GAME
        self.save()

    def create_new_game(self):
        game_id = hashlib.md5(str(int(self.id) + random.randint(-1000000, 1000000)).encode('utf-8')).hexdigest()
        self.game = game.Game(game_id)
        self.game.to_waiting_start(self)
        self.state = PlayerState.WAITING_START_GAME
        self.save()

        return game_id

    def request_game_code_to_connect(self):
        print('into method')
        self.load()
        print('loaded')
        self.state = PlayerState.REQUEST_GAME_CODE_TO_CONNECT
        print('set state')
        self.save()
        print('saved')

    def is_request_game_code_to_connect(self):
        self.load()
        return self.state == PlayerState.REQUEST_GAME_CODE_TO_CONNECT

    def connect_to_game(self, game_id):
        self.game = game_id
        self.state = PlayerState.WAITING_START_GAME
        self.save()

    def move_to_trash(self, card_number):
        logger = logging.getLogger('hanabigame.player.move_to_trash')
        logger.info('start')
        self.load()
        logger.info('loaded')
        trashed_card_number = self.hand.pop(card_number)
        logger.info('get trashed card')
        self.game.add_to_trash(trashed_card_number)
        logger.info('add to trash')
        new_card = self.game.take_card()
        logger.info('get new card')
        self.hand.append(new_card)
        logger.info('add new card')
        self.save()
        logger.info('save player')
        return num_to_card(trashed_card_number)

    def move_to_table(self, card_number):
        logger = logging.getLogger('hanabigame.player.move_to_table')
        logger.info('start')
        self.load()
        logger.info('loaded')
        put_card_number = self.hand.pop(card_number)
        logger.info('get put card')
        success = self.game.add_to_table(put_card_number)
        logger.info('add to table')
        new_card = self.game.take_card()
        logger.info('get new card')
        self.hand.append(new_card)
        logger.info('add new card')
        self.save()
        logger.info('save player')
        return num_to_card(put_card_number), success

    def is_request_card_number_to_trash(self):
        self.load()
        return self.state == PlayerState.REQUEST_MOVE_TO_TRASH

    def is_request_card_number_to_put(self):
        self.load()
        return self.state == PlayerState.REQUEST_MOVE_TO_TABLE

    def is_request_hint_recipient(self):
        self.load()
        return self.state == PlayerState.REQUEST_HINT_RECIPIENT

    def is_request_hint_type(self):
        self.load()
        return PlayerState.REQUEST_HINT_TYPE_ONE <= self.state <= PlayerState.REQUEST_HINT_TYPE_FIVE

    def is_request_hint_color(self):
        self.load()
        return PlayerState.REQUEST_HINT_ONE_COLOR <= self.state <= PlayerState.REQUEST_HINT_FIVE_COLOR

    def is_request_hint_value(self):
        logger = logging.getLogger('hanabigame.player.is_request_hint_value')
        logger.info('start')
        self.load()
        return PlayerState.REQUEST_HINT_ONE_VALUE <= self.state <= PlayerState.REQUEST_HINT_FIVE_VALUE

    def get_recipient_hint_number(self):
        self.load()
        if PlayerState.REQUEST_HINT_ONE_COLOR <= self.state <= PlayerState.REQUEST_HINT_FIVE_COLOR:
            return int(self.state - PlayerState.REQUEST_HINT_ONE_COLOR)
        return int(self.state - PlayerState.REQUEST_HINT_ONE_VALUE)

    def get_card_numbers_with_color(self, color):
        logger = logging.getLogger('hanabigame.player.get_card_numbers_with_color')
        logger.info('start')
        self.load()
        logger.info('loaded')
        card_numbers = self.hand.get_card_numbers_with_color(color)
        logger.info('get card numbers')
        return card_numbers

    def get_card_numbers_with_value(self, value):
        logger = logging.getLogger('hanabigame.player.get_card_numbers_with_value')
        logger.info('start')
        self.load()
        logger.info('loaded')
        card_numbers = self.hand.get_card_numbers_with_value(value)
        logger.info('get card numbers')
        return card_numbers

    def start_game(self, hand):
        print('in Player.start_game')
        self.load()
        print('loaded')

        self.state = PlayerState.PLAYING
        print('set state')
        self.hand = hand
        print('set hand')

        self.save()
        print('save player')

import random
import logging

import database
import player
from sequence import Sequence, previous_card, next_card, init_list


class GameState:
    NOT_START = 0
    WAITING_START = 1
    TURN_PLAYER_ONE = 5
    TURN_PLAYER_TWO = 6
    TURN_PLAYER_THREE = 7
    TURN_PLAYER_FOUR = 8
    TURN_PLAYER_FIVE = 9
    FINISH = 10


class Game:
    class ConnectResponse:
        ERROR = 0
        OK = 1
        OK_AND_START = 2

    def __init__(self, game_id):
        self.id = str(game_id)
        self.loaded = False

        self.state = GameState.NOT_START
        self.stack = None
        self.table = None
        self.trash = None
        self.hints = 0
        self.lives = 0
        self.players = []

    def load(self):
        if not self.loaded:
            response = database.get_game_info(self.id)
            if 'Item' in response:
                self.state = response['Item']['state']
                self.stack = Sequence.from_str(response['Item'].get('stack', None))
                self.table = Sequence.from_str(response['Item'].get('table', None))
                self.trash = Sequence.from_str(response['Item'].get('trash', None))

                for i in range(1, 6):
                    player_id = response['Item'].get('player' + str(i), None)
                    if player_id is not None:
                        self.players.append(player.Player(player_id))

                self.hints = response['Item'].get('hints', 0)
                self.lives = response['Item'].get('lives', 0)

            self.loaded = True

    def save(self):
        player_to_id = {('player' + str(k + 1), player.id) for k, player in enumerate(self.players)}
        stack = self.stack.to_str() if self.stack is not None else ''
        table = self.table.to_str() if self.table is not None else ''
        trash = self.trash.to_str() if self.trash is not None else ''
        database.set_game_info(self.id, self.state, stack, table, trash, player_to_id, self.hints, self.lives)

    def get_table_output(self):
        self.load()
        return self.table.to_output() if self.table is not None else '', self.hints, self.lives

    def get_trash_output(self):
        self.load()
        return self.trash.to_output() if self.trash is not None else ''

    def finish(self):
        self.load()
        for player in self.players:
            player.finish()

        database.finish_game(self.id)

    def to_waiting_start(self, player):
        self.players.append(player)
        self.state = GameState.WAITING_START
        self.save()

    def connect_player(self, player):
        logger = logging.getLogger('hanabigame.game.connect_player')
        logger.info('start')
        self.load()
        logger.info('load')
        if self.state != GameState.WAITING_START:
            logger.info('return error')
            return Game.ConnectResponse.ERROR, []

        self.players.append(player)
        player.connect_to_game(self)
        self.save()
        logger.info('saved game')
        return (Game.ConnectResponse.OK if len(self.players) < 5 else Game.ConnectResponse.OK_AND_START), self.players

    def start(self):
        print('in Game.start')
        self.load()
        print('loaded')

        lst = init_list()
        random.shuffle(lst)
        cnt = 5 if len(self.players) < 4 else 4
        print('generate stack')

        for i, p in enumerate(self.players):
            p.start_game(Sequence(lst[i * cnt:(i + 1) * cnt]))
        print('players started game')

        self.stack = Sequence(lst[cnt * len(self.players):])
        self.table = Sequence([])
        self.trash = Sequence([])
        self.state = GameState.TURN_PLAYER_ONE

        self.hints = 8
        self.lives = 3

        self.save()
        print('save game')

        return self.players

    def take_card(self):
        logger = logging.getLogger('hanabigame.game.take_card')
        logger.info('start')
        self.load()
        logger.info('loaded')
        taked_card = self.stack.pop()
        logger.info('get taked card')
        self.save()
        logger.info('save game')
        return taked_card

    def add_to_trash(self, card_number):
        logger = logging.getLogger('hanabigame.game.add_to_trash')
        logger.info('start')
        self.load()
        logger.info('loaded')
        if self.trash is not None:
            self.trash.append(card_number)
        else:
            self.trash = Sequence([card_number])
        logger.info('add card to trash')
        self.save()
        logger.info('save game')

    def add_to_table(self, card_number):
        logger = logging.getLogger('hanabigame.game.add_to_table')
        logger.info('start')
        self.load()
        logger.info('loaded')
        prev_card_number = previous_card(card_number)
        logger.info('get prev card number')
        if prev_card_number is None or (self.table is not None and self.table.contains(prev_card_number)):
            logger.info('success branch')
            if prev_card_number is None:
                logger.info('first card')
                if self.table is not None:
                    self.table.append(card_number)
                else:
                    self.table = Sequence([card_number])
            else:
                logger.info('not first card')
                index = self.table.index(prev_card_number)
                self.table.pop(index)
                self.table.append(card_number)

            if next_card(card_number) is None:
                self.hints = min(self.hints + 1, 8)
            self.save()
            return True
        else:
            logger.info('fail branch')
            self.add_to_trash(card_number)
            logger.info('add to trash')
            self.lives -= 1
            logger.info('decrease lives')
            self.save()
            return False

    def hint_color(self, recipient_number, color):
        logger = logging.getLogger('hanabigame.game.hint_color')
        logger.info('start')
        self.load()
        logger.info('loaded')
        print(recipient_number)
        print(self.players)
        recipient = self.players[recipient_number]
        print(recipient.get_name())
        print(recipient)
        print(recipient.id)
        card_numbers = recipient.get_card_numbers_with_color(color)
        logger.info('get card numbers ' + ','.join(map(str, card_numbers)))
        self.hints -= 1
        logger.info('decrease hints')
        return card_numbers

    def hint_value(self, recipient_number, value):
        logger = logging.getLogger('hanabigame.game.hint_value')
        logger.info('start')
        self.load()
        logger.info('loaded')
        print(recipient_number)
        print(self.players)
        recipient = self.players[recipient_number]
        print(recipient.get_name())
        print(recipient)
        print(recipient.id)
        card_numbers = recipient.get_card_numbers_with_value(value)
        logger.info('get card numbers ' + ','.join(map(str, card_numbers)))
        self.hints -= 1
        logger.info('decrease hints')
        return card_numbers

    def next_turn(self):
        logger = logging.getLogger('hanabigame.game.next_turn')
        logger.info('start')
        self.load()
        logger.info('loaded')
        self.state += 1
        if self.state - len(self.players) == 5:
            self.state = GameState.TURN_PLAYER_ONE
        logger.info('set new state')
        self.save()
        logger.info('save game')
        return self.state - 5

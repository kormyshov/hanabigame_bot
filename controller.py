import logging

import keyboards
import constants
from abstract_base import AbstractBase
from abstract_viewer import AbstractViewer
from player import Player
from game import Game, ConnectionResult, GameDoesntInit


class Controller:
    def __init__(self, database: AbstractBase, viewer: AbstractViewer):
        self.database = database
        self.viewer = viewer

    def create_new_game(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.create_new_game')
        logger.info('start')
        game = Game()
        game_id = game.init_game(player)
        logger.info('init game with game_id = ' + game_id)
        game.set_database(self.database)
        game.save()
        logger.info('save game')
        self.viewer.view(player.id, constants.GAME_CREATED)
        self.viewer.view(player.id, game_id, keyboards.get_waiting_second_player())

    def request_id_for_connect_to_game(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_id_for_connect_to_game')
        logger.info('start')
        player.request_game_code_to_connect()
        logger.info('player requested')
        self.viewer.view(player.id, constants.ENTER_GAME_CODE_TO_CONNECT, keyboards.get_reject_connect_game())

    def reject_connect_to_game(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_connect_to_game')
        logger.info('start')
        player.reject_connect_to_game()
        logger.info('player rejected connecting')
        self.viewer.view(player.id, constants.ONBOARDING, keyboards.get_start_game())

    def connect_to_game(self, player: Player, game_id: str) -> None:
        logger = logging.getLogger('hanabigame.main.connect_to_game')
        logger.info('start with game_id = ' + game_id)
        game = Game()
        game.set_id(game_id)
        game.set_database(self.database)
        game.load()
        logger.info('get game')
        try:
            response = game.connect_player(player)
            logger.info('get connection result')
            for p in game.players[:-1]:
                self.viewer.view(
                    p.id,
                    constants.PLAYER_CONNECT_TO_GAME.format(player.name),
                    keyboards.get_waiting_start_game(),
                )
            logger.info('output other players')
            self.viewer.view(
                player.id,
                constants.YOU_HAS_BEEN_CONNECTED_TO_GAME,
                keyboards.get_waiting_start_game(),
            )
            logger.info('output current player')
            if response == ConnectionResult.OK_AND_START:
                logger.info('go to start game')
                self.start_game()
            game.save()
            logger.info('game saved')
        except GameDoesntInit:
            logger.info('wrong code of game')
            self.viewer.view(
                player.id,
                constants.THERE_IS_NO_GAME_WITH_THIS_CODE,
                keyboards.get_reject_connect_game(),
            )

    def start_game(self) -> None:
        logger = logging.getLogger('hanabigame.main.start_game')
        logger.info('start')
        Game().start()
        logger.info('game started')
        for i, p in enumerate(Game().players):
            self.viewer.view(p.id, constants.GAME_STARTED)
        logger.info('output messages')
        self.turn_player(0)
        logger.info('end')

    def turn_player(self, num: int) -> None:
        logger = logging.getLogger('hanabigame.main.turn_player')
        logger.info('start')
        for i, p in enumerate(Game().players):
            logger.info('go for')
            if i == num:
                self.viewer.view(p.id, constants.YOUR_TURN, keyboards.get_turn())
            else:
                self.viewer.view(
                    p.id,
                    constants.TURN_ANOTHER_PLAYER.format(Game().players[num].get_name()),
                    keyboards.get_waiting_turn(),
                )
        logger.info('end')

    def request_for_confirm_finish_game(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_for_confirm_finish_game')
        logger.info('start')
        player.confirm_finish_game()
        logger.info('player confirmed')
        self.viewer.view(player.id, constants.ARE_YOU_SURE, keyboards.get_confirm_finish_game())

    def reject_finish_game(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.reject_finish_game')
        logger.info('start')
        player.reject_finish_game()
        logger.info('player rejected finishing')
        if player.is_playing():
            if Game().is_player_turn(player):
                self.viewer.view(player.id, constants.LETS_CONTINUE, keyboards.get_turn())
            else:
                self.viewer.view(player.id, constants.LETS_CONTINUE, keyboards.get_waiting_turn())
        else:
            if len(Game().players) == 1:
                self.viewer.view(player.id, constants.LETS_CONTINUE, keyboards.get_waiting_second_player())
            else:
                self.viewer.view(player.id, constants.LETS_CONTINUE, keyboards.get_waiting_start_game())

    def confirm_finish_game(self) -> None:
        logger = logging.getLogger('hanabigame.main.confirm_finish_game')
        logger.info('start')
        Game().finish()
        logger.info('game finished')
        for player in Game().players:
            self.viewer.view(player.id, constants.GAME_FINISHED, keyboards.get_start_game())

    def look_table(self, player: Player) -> None:
        table, hints, lives = Game().get_table_info()
        output = str(table) if table.len() != 0 else constants.EMPTY_TABLE
        output += '\n' + constants.HINTS + ': ' + str(hints)
        output += '\n' + constants.LIVES + ': ' + str(lives)
        self.viewer.view(player.id, output)

    def look_trash(self, player):
        trash = Game().get_trash_cards()
        self.viewer.view(player.id, str(trash) if trash.len() != 0 else constants.EMPTY_TRASH)

    def look_hands(self, player, game):
        logger = logging.getLogger('hanabigame.main.look_hands')
        logger.info('start')
        game.load()
        logger.info('loaded game')
        for p in game.players:
            logger.info('get player')
            if p.id != player.id:
                logger.info('it is another player')
                hand_str = p.get_hand_output()
                logger.info('got hand_str')
                self.viewer.view(player.id, p.get_name() + '\n' + hand_str if hand_str != '' else constants.EMPTY_HAND)

    def request_for_move_to_trash(self, player):
        logger = logging.getLogger('hanabigame.main.request_for_move_to_trash')
        logger.info('start')
        count_of_cards = player.request_move_to_trash()
        logger.info('got count_of_cards')
        self.viewer.view(player.id, constants.ENTER_CARD_NUMBER, keyboards.get_request_card_number(count_of_cards))

    def move_to_trash(self, player, game, card_number_str):
        logger = logging.getLogger('hanabigame.main.move_to_trash')
        logger.info('start')
        trashed_card = player.move_to_trash(int(card_number_str) - 1)
        logger.info('moved to trash and got trashed crad')
        for p in game.players:
            logger.info('get player')
            self.viewer.view(
                p.id,
                constants.PLAYER_HAS_TRASHED_CARD.format(
                    player.name if player.id != p.id else constants.YOU,
                    trashed_card,
                ),
            )

        player_number = game.next_turn()
        logger.info('next turn')
        self.turn_player(game.players, int(player_number))

    def request_for_move_to_table(self, player):
        logger = logging.getLogger('hanabigame.main.request_for_move_to_table')
        logger.info('start')
        count_of_cards = player.request_move_to_table()
        logger.info('got count_of_cards')
        self.viewer.view(player.id, constants.ENTER_CARD_NUMBER, keyboards.get_request_card_number(count_of_cards))

    def move_to_table(self, player, game, card_number_str):
        logger = logging.getLogger('hanabigame.main.move_to_table')
        logger.info('start')
        put_card, success = player.move_to_table(int(card_number_str) - 1)
        logger.info('moved to table and got put card')
        for p in game.players:
            logger.info('get player')
            if success:
                self.viewer.view(
                    p.id,
                    constants.PLAYER_HAS_PUT_CARD.format(
                        player.name if player.id != p.id else constants.YOU,
                        put_card,
                    ),
                )
            else:
                self.viewer.view(
                    p.id,
                    constants.PLAYER_TRIED_TO_PUT_CARD.format(
                        player.name if player.id != p.id else constants.YOU,
                        put_card,
                    ),
                )

        player_number = game.next_turn()
        logger.info('next turn')
        self.turn_player(game.players, int(player_number))

    def request_for_hint_recipient(self, player, game):
        logger = logging.getLogger('hanabigame.main.request_for_hint_recipient')
        logger.info('start')
        game.load()
        names = [p.get_name() for p in game.players if p.id != player.id]
        logger.info('get names ' + ', '.join(names))
        if len(names) > 1:
            logger.info('many players')
            player.request_hint_recipient()
            self.viewer.view(player.id, constants.ENTER_PLAYER_NAME, keyboards.get_request_player_name(names))
        else:
            self.request_for_type_of_hint(player, game, names[0])

    def request_for_type_of_hint(self, player, game, recipient_name):
        logger = logging.getLogger('hanabigame.main.request_for_type_of_hint')
        logger.info('start')
        game.load()
        recipient_number = 0
        for i, p in enumerate(game.players):
            if p.get_name() == recipient_name:
                recipient_number = i
        player.request_hint_type(recipient_number)
        logger.info('switch player state')
        self.viewer.view(player.id, constants.ENTER_TYPE_OF_HINT, keyboards.type_of_hint)

    def request_for_hint_color(self, player):
        logger = logging.getLogger('hanabigame.main.request_for_hint_color')
        logger.info('start')
        player.request_hint_color()
        logger.info('switch player state')
        self.viewer.view(player.id, constants.ENTER_COLOR, keyboards.colors)

    def request_for_hint_value(self, player):
        logger = logging.getLogger('hanabigame.main.request_for_hint_value')
        logger.info('start')
        player.request_hint_value()
        logger.info('switch player state')
        self.viewer.view(player.id, constants.ENTER_VALUE, keyboards.values)

    def hint_color(self, player, game, color):
        logger = logging.getLogger('hanabigame.main.hint_color')
        logger.info('start')
        recipient_number = player.get_recipient_hint_number()
        logger.info('get recipient number = ' + str(recipient_number) + ' with type ' + str(type(recipient_number)))
        game.load()
        card_numbers = game.hint_color(recipient_number, color)
        logger.info('get card numbers ' + ','.join(map(str, card_numbers)))
        for i, p in enumerate(game.players):
            if i == recipient_number:
                self.viewer.view(
                    p.id,
                    constants.PLAYER_HINT_COLOR_TO_YOU.format(
                        player.get_name(),
                        color,
                        ', '.join(map(str, card_numbers)),
                    ),
                )
            elif p.id == player.id:
                self.viewer.view(p.id, constants.YOU_HAS_HINT.format(game.players[recipient_number].get_name()))
            else:
                self.viewer.view(
                    p.id,
                    constants.PLAYER_HINT_COLOR_TO_OTHER.format(
                        player.get_name(),
                        game.players[recipient_number].get_name(),
                        color,
                        ', '.join(map(str, card_numbers)),
                    ),
                )

        player_number = game.next_turn()
        logger.info('next turn')
        self.turn_player(game.players, int(player_number))

    def hint_value(self, player, game, value):
        logger = logging.getLogger('hanabigame.main.hint_value')
        logger.info('start')
        recipient_number = player.get_recipient_hint_number()
        logger.info('get recipient number = ' + str(recipient_number) + ' with type ' + str(type(recipient_number)))
        game.load()
        card_numbers = game.hint_value(recipient_number, value)
        logger.info('get card numbers ' + ','.join(map(str, card_numbers)))
        for i, p in enumerate(game.players):
            if i == recipient_number:
                self.viewer.view(
                    p.id,
                    constants.PLAYER_HINT_VALUE_TO_YOU.format(
                        player.get_name(),
                        value,
                        ', '.join(map(str, card_numbers)),
                    ),
                )
            elif p.id == player.id:
                self.viewer.view(p.id, constants.YOU_HAS_HINT.format(game.players[recipient_number].get_name()))
            else:
                self.viewer.view(
                    p.id,
                    constants.PLAYER_HINT_VALUE_TO_OTHER.format(
                        player.get_name(),
                        game.players[recipient_number].get_name(),
                        value,
                        ', '.join(map(str, card_numbers)),
                    ),
                )

        player_number = game.next_turn()
        logger.info('next turn')
        self.turn_player(game.players, int(player_number))

    def operate(self, player_id: str, player_name: str, text: str):
        logger = logging.getLogger('hanabigame.main.message_reply')
        logger.info('start with message.text = ' + text)
        player = Player(player_id, self.database)
        logger.info('get Player')
        player.set_name(player_name)
        logger.info('set player name')
        game_id = player.get_game_id()
        logger.info('get game id = ' + str(game_id))

        if game_id is None or game_id == 'None':
            logger.info('in if with game_id is None')
            if text == constants.CREATE_GAME and player.is_not_playing():
                logger.info('branch create_new_game')
                self.create_new_game(player)
            elif text == constants.CONNECT_TO_GAME and player.is_not_playing():
                logger.info('branch request_id_for_connect_to_game')
                self.request_id_for_connect_to_game(player)
            elif text == constants.DONT_CONNECT_TO_GAME and player.is_request_game_code_to_connect():
                logger.info('branch reject_connect_to_game')
                self.reject_connect_to_game(player)
            else:
                if player.is_request_game_code_to_connect():
                    logger.info('branch connect_to_game')
                    self.connect_to_game(player, text)
        else:
            logger.info('in if with game_id is not None')
            game = Game()
            game.set_id(game_id)
            game.set_database(self.database)
            game.load()
            if text == constants.FINISH_GAME:
                logger.info('branch request_for_confirm_finish_game')
                self.request_for_confirm_finish_game(player)
            elif text == constants.YES_FINISH_GAME:
                logger.info('branch confirm_finish_game')
                self.confirm_finish_game()
                return
            elif text == constants.NO_CONTINUE_GAME:
                logger.info('branch reject_finish_game')
                self.reject_finish_game(player)
            elif text == constants.START_GAME:
                logger.info('branch start_game')
                self.start_game()
            elif text == constants.LOOK_TABLE:
                self.look_table(player)
            elif text == constants.LOOK_TRASH:
                self.look_trash(player)
            elif text == constants.LOOK_HANDS:
                self.look_hands(player)
            elif text == constants.TRASH:
                self.request_for_move_to_trash(player)
            elif text == constants.PUT:
                self.request_for_move_to_table(player)
            elif text == constants.HINT:
                self.request_for_hint_recipient(player)
            elif text == constants.COLOR:
                self.request_for_hint_color(player)
            elif text == constants.VALUE:
                self.request_for_hint_value(player)
            else:
                if player.is_request_card_number_to_trash():
                    self.move_to_trash(player, text)
                if player.is_request_card_number_to_put():
                    self.move_to_table(player, text)
                if player.is_request_hint_recipient():
                    self.request_for_type_of_hint(player, text)
                if player.is_request_hint_color():
                    self.hint_color(player, text)
                if player.is_request_hint_value():
                    self.hint_value(player, text)

            game.save()

import logging

import keyboards
import constants
from abstract_base import AbstractBase
from abstract_viewer import AbstractViewer
from player import Player
from game import Game, ConnectionResult, GameDoesntInit, GameIsEnded


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
                self.start_game(game)
            game.save()
            logger.info('game saved')
        except GameDoesntInit:
            logger.info('wrong code of game')
            self.viewer.view(
                player.id,
                constants.THERE_IS_NO_GAME_WITH_THIS_CODE,
                keyboards.get_reject_connect_game(),
            )

    def start_game(self, game: Game) -> None:
        logger = logging.getLogger('hanabigame.main.start_game')
        logger.info('start')
        game.start()
        logger.info('game started')
        self.broadcast(constants.GAME_STARTED, game)
        logger.info('output messages')
        self.turn_player(game, 0)
        logger.info('end')

    def turn_player(self, game: Game, num: int) -> None:
        logger = logging.getLogger('hanabigame.main.turn_player')
        logger.info('start with num = ' + str(num))
        for i, p in enumerate(game.players):
            logger.info('go for i = ' + str(i))
            if i == num:
                logger.info('into i == num')
                self.viewer.view(p.id, constants.YOUR_TURN, keyboards.get_turn(game.hints > 0))
            else:
                logger.info('into i != num')
                logger.info('game = ' + str(game))
                logger.info('players len = ' + str(len(game.players)))
                try:
                    logger.info('player = ' + str(game.players[num]))
                except Exception as e:
                    logger.info(str(e))
                self.viewer.view(
                    p.id,
                    constants.TURN_ANOTHER_PLAYER.format(game.players[num].get_name()),
                    keyboards.get_waiting_turn(),
                )
        logger.info('end')

    def request_for_confirm_finish_game(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_for_confirm_finish_game')
        logger.info('start')
        player.confirm_finish_game()
        logger.info('player confirmed')
        self.viewer.view(player.id, constants.ARE_YOU_SURE, keyboards.get_confirm_finish_game())

    def reject_finish_game(self, game: Game, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.reject_finish_game')
        logger.info('start')
        player.reject_finish_game()
        logger.info('player rejected finishing')
        if player.is_playing():
            if game.is_player_turn(player):
                self.viewer.view(player.id, constants.LETS_CONTINUE, keyboards.get_turn(game.hints > 0))
            else:
                self.viewer.view(player.id, constants.LETS_CONTINUE, keyboards.get_waiting_turn())
        else:
            if len(game.players) == 1:
                self.viewer.view(player.id, constants.LETS_CONTINUE, keyboards.get_waiting_second_player())
            else:
                self.viewer.view(player.id, constants.LETS_CONTINUE, keyboards.get_waiting_start_game())

    def confirm_finish_game(self, game: Game) -> None:
        logger = logging.getLogger('hanabigame.main.confirm_finish_game')
        logger.info('start')
        game.finish()
        logger.info('game finished')
        for player in game.players:
            self.viewer.view(player.id, constants.GAME_FINISHED, keyboards.get_start_game())

    def look_table(self, game: Game, player: Player) -> None:
        table, hints, lives = game.get_table_info()
        output = str(table) if table.len() != 0 else constants.EMPTY_TABLE
        output += '\n' + constants.HINTS + ': ' + str(hints)
        output += '\n' + constants.LIVES + ': ' + str(lives)
        self.viewer.view(player.id, output)

    def look_trash(self, game: Game, player: Player) -> None:
        trash = game.get_trash_cards()
        self.viewer.view(player.id, str(trash) if trash.len() != 0 else constants.EMPTY_TRASH)

    def look_hands(self, game: Game, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.look_hands')
        logger.info('start')
        for p in game.players:
            logger.info('get player')
            if p.id != player.id:
                logger.info('it is another player')
                hand = p.get_hand_cards()
                logger.info('got hand_str')
                self.viewer.view(
                    player.id,
                    p.get_name() + '\n' + str(hand) if hand.len() != 0 else constants.EMPTY_HAND,
                )

    def request_for_move_to_trash(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_for_move_to_trash')
        logger.info('start')
        count_of_cards = player.request_move_to_trash()
        logger.info('got count_of_cards')
        self.viewer.view(player.id, constants.ENTER_CARD_NUMBER, keyboards.get_request_card_number(count_of_cards))

    def move_to_trash(self, game: Game, player: Player, card_number: str) -> None:
        logger = logging.getLogger('hanabigame.main.move_to_trash')
        logger.info('start')
        trashed_card = game.move_to_trash(player, int(card_number) - 1)
        logger.info('moved to trash and got trashed card')
        self.broadcast(
            constants.PLAYER_HAS_TRASHED_CARD.format(player.name, str(trashed_card)),
            game,
            constants.PLAYER_HAS_TRASHED_CARD.format(constants.YOU, str(trashed_card)),
            player.id,
        )
        self.next_turn(game)

    def request_for_move_to_table(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_for_move_to_table')
        logger.info('start')
        count_of_cards = player.request_move_to_table()
        logger.info('got count_of_cards')
        self.viewer.view(player.id, constants.ENTER_CARD_NUMBER, keyboards.get_request_card_number(count_of_cards))

    def move_to_table(self, game: Game, player: Player, card_number: str) -> None:
        logger = logging.getLogger('hanabigame.main.move_to_table')
        logger.info('start')
        try:
            success, put_card = game.move_to_table(player, int(card_number) - 1)
            logger.info('moved to table and got put card')
            if success:
                self.broadcast(
                    constants.PLAYER_HAS_PUT_CARD.format(player.name, str(put_card)),
                    game,
                    constants.PLAYER_HAS_PUT_CARD.format(constants.YOU, str(put_card)),
                    player.id,
                )
            else:
                self.broadcast(
                    constants.PLAYER_TRIED_TO_PUT_CARD.format(player.name, str(put_card)),
                    game,
                    constants.PLAYER_TRIED_TO_PUT_CARD.format(constants.YOU, str(put_card)),
                    player.id,
                )
            self.next_turn(game)
        except GameIsEnded:
            self.broadcast(
                constants.GAME_FAILED.format(player.name),
                game,
                constants.GAME_FAILED.format(constants.YOU),
                player.id,
            )
            self.broadcast(constants.SCORE.format('0'), game)
            self.confirm_finish_game(game)
            raise GameIsEnded

    def broadcast(self, message: str, game: Game, self_message: str = None, player_id: str = None):
        for p in game.players:
            self.viewer.view(p.id, message if player_id is None or player_id != p.id else self_message)

    def next_turn(self, game: Game):
        try:
            player_number = game.next_turn()
            self.turn_player(game, player_number)
        except GameIsEnded:
            score = game.get_score()
            self.broadcast(constants.SCORE.format(str(score)), game)
            self.confirm_finish_game(game)

    def request_for_hint_recipient(self, game: Game, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_for_hint_recipient')
        logger.info('start')
        names = [p.get_name() for p in game.players if p.id != player.id]
        logger.info('get names ' + ', '.join(names))
        if len(names) > 1:
            logger.info('many players')
            player.request_hint_recipient()
            self.viewer.view(player.id, constants.ENTER_PLAYER_NAME, keyboards.get_request_player_name(names))
        else:
            self.request_for_type_of_hint(game, player, names[0])

    def request_for_type_of_hint(self, game: Game, player: Player, recipient_name: str) -> None:
        logger = logging.getLogger('hanabigame.main.request_for_type_of_hint')
        logger.info('start')
        recipient_number = 0
        for i, p in enumerate(game.players):
            if p.get_name() == recipient_name:
                recipient_number = i
        player.request_hint_type(recipient_number)
        logger.info('switch player state')
        self.viewer.view(player.id, constants.ENTER_TYPE_OF_HINT, keyboards.get_type_of_hint())

    def request_for_hint_color(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_for_hint_color')
        logger.info('start')
        player.request_hint_color()
        logger.info('switch player state')
        self.viewer.view(player.id, constants.ENTER_COLOR, keyboards.get_colors())

    def request_for_hint_value(self, player: Player) -> None:
        logger = logging.getLogger('hanabigame.main.request_for_hint_value')
        logger.info('start')
        player.request_hint_value()
        logger.info('switch player state')
        self.viewer.view(player.id, constants.ENTER_VALUE, keyboards.get_values())

    def hint_color(self, game: Game, player: Player, color: str) -> None:
        logger = logging.getLogger('hanabigame.main.hint_color')
        logger.info('start')
        recipient_number = player.get_recipient_hint_number()
        logger.info('get recipient number = ' + str(recipient_number) + ' with type ' + str(type(recipient_number)))
        card_numbers = game.hint_color(player, recipient_number, color)
        logger.info('get card numbers ' + ','.join(map(str, card_numbers)))
        self.broadcast_hint(
            game,
            player,
            recipient_number,
            constants.PLAYER_HINT_COLOR_TO_YOU.format(player.get_name(), color, ', '.join(map(str, card_numbers))),
            constants.PLAYER_HINT_COLOR_TO_OTHER.format(
                player.get_name(),
                game.players[recipient_number].get_name(),
                color,
                ', '.join(map(str, card_numbers)),
            ),
            constants.YOU_HAS_HINT.format(game.players[recipient_number].get_name()),
        )
        self.next_turn(game)

    def hint_value(self, game: Game, player: Player, value: str) -> None:
        logger = logging.getLogger('hanabigame.main.hint_value')
        logger.info('start')
        recipient_number = player.get_recipient_hint_number()
        logger.info('get recipient number = ' + str(recipient_number) + ' with type ' + str(type(recipient_number)))
        card_numbers = game.hint_value(player, recipient_number, value)
        logger.info('get card numbers ' + ','.join(map(str, card_numbers)))
        self.broadcast_hint(
            game,
            player,
            recipient_number,
            constants.PLAYER_HINT_VALUE_TO_YOU.format(player.get_name(), value, ', '.join(map(str, card_numbers))),
            constants.PLAYER_HINT_VALUE_TO_OTHER.format(
                player.get_name(),
                game.players[recipient_number].get_name(),
                value,
                ', '.join(map(str, card_numbers)),
            ),
            constants.YOU_HAS_HINT.format(game.players[recipient_number].get_name()),
        )
        self.next_turn(game)

    def broadcast_hint(self, game: Game, player: Player, recipient_number: int,
                       hint: str, common_hint: str, self_hint: str):
        for i, p in enumerate(game.players):
            if i == recipient_number:
                self.viewer.view(p.id, hint)
            elif p.id == player.id:
                self.viewer.view(p.id, self_hint)
            else:
                self.viewer.view(p.id, common_hint)

    def goto_menu(self, game: Game, player: Player):
        player.set_playing_state()
        self.viewer.view(player.id, constants.YOUR_TURN, keyboards.get_turn(game.hints > 0))

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
                self.confirm_finish_game(game)
                return
            elif text == constants.NO_CONTINUE_GAME:
                logger.info('branch reject_finish_game')
                self.reject_finish_game(game, player)
            elif text == constants.START_GAME:
                logger.info('branch start_game')
                self.start_game(game)
                game.save()
                return
            elif text == constants.LOOK_TABLE:
                self.look_table(game, player)
            elif text == constants.LOOK_TRASH:
                self.look_trash(game, player)
            elif text == constants.LOOK_HANDS:
                self.look_hands(game, player)
            elif text == constants.TRASH:
                logger.info('branch request_for_move_to_trash')
                self.request_for_move_to_trash(player)
            elif text == constants.PUT:
                logger.info('branch request_for_move_to_table')
                self.request_for_move_to_table(player)
            elif text == constants.HINT:
                self.request_for_hint_recipient(game, player)
            elif text == constants.COLOR:
                self.request_for_hint_color(player)
            elif text == constants.VALUE:
                self.request_for_hint_value(player)
            elif text == constants.BACK:
                self.goto_menu(game, player)
            else:
                if player.is_request_card_number_to_trash():
                    logger.info('branch move_to_trash')
                    self.move_to_trash(game, player, text)
                elif player.is_request_card_number_to_put():
                    logger.info('branch move_to_put')
                    try:
                        self.move_to_table(game, player, text)
                    except GameIsEnded:
                        return
                elif player.is_request_hint_recipient():
                    self.request_for_type_of_hint(game, player, text)
                elif player.is_request_hint_color():
                    self.hint_color(game, player, text)
                elif player.is_request_hint_value():
                    self.hint_value(game, player, text)

            game.save()
        player.save()

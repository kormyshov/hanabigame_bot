import keyboards
import constants
from logging_decorator import logger
from abstract_base import AbstractBase
from abstract_viewer import AbstractViewer
from player import Player
from game import Game, ConnectionResult, GameDoesntInit, GameIsEnded


class Controller:
    def __init__(self, database: AbstractBase, viewer: AbstractViewer):
        self.database = database
        self.viewer = viewer

    @logger
    def create_new_game(self, player: Player) -> None:
        game = Game()
        game_id = game.init_game(player)
        game.set_database(self.database)
        game.save()
        self.viewer.view(player.id, constants.GAME_CREATED)
        self.viewer.view(player.id, game_id, keyboards.get_waiting_second_player())

    @logger
    def request_id_for_connect_to_game(self, player: Player) -> None:
        player.request_game_code_to_connect()
        self.viewer.view(player.id, constants.ENTER_GAME_CODE_TO_CONNECT, keyboards.get_reject_connect_game())

    @logger
    def reject_connect_to_game(self, player: Player) -> None:
        player.reject_connect_to_game()
        self.viewer.view(player.id, constants.ONBOARDING, keyboards.get_start_game())

    @logger
    def connect_to_game(self, player: Player, game_id: str) -> None:
        game = Game()
        game.set_id(game_id)
        game.set_database(self.database)
        game.load()
        try:
            response = game.connect_player(player)
            for p in game.players[:-1]:
                self.viewer.view(
                    p.id,
                    constants.PLAYER_CONNECT_TO_GAME.format(player.name),
                    keyboards.get_waiting_start_game(),
                )
            self.viewer.view(
                player.id,
                constants.YOU_HAS_BEEN_CONNECTED_TO_GAME,
                keyboards.get_waiting_start_game(),
            )
            if response == ConnectionResult.OK_AND_START:
                self.start_game(game)
            game.save()
        except GameDoesntInit:
            self.viewer.view(
                player.id,
                constants.THERE_IS_NO_GAME_WITH_THIS_CODE,
                keyboards.get_reject_connect_game(),
            )

    @logger
    def start_game(self, game: Game) -> None:
        game.start()
        self.broadcast(constants.GAME_STARTED, game)
        self.turn_player(game, 0)

    @logger
    def turn_player(self, game: Game, num: int) -> None:
        for i, p in enumerate(game.players):
            if i == num:
                self.viewer.view(p.id, constants.YOUR_TURN, keyboards.get_turn(game.hints > 0))
            else:
                self.viewer.view(
                    p.id,
                    constants.TURN_ANOTHER_PLAYER.format(game.players[num].get_name()),
                    keyboards.get_waiting_turn(),
                )

    @logger
    def request_for_confirm_finish_game(self, player: Player) -> None:
        player.confirm_finish_game()
        self.viewer.view(player.id, constants.ARE_YOU_SURE, keyboards.get_confirm_finish_game())

    @logger
    def reject_finish_game(self, game: Game, player: Player) -> None:
        player.reject_finish_game()
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

    @logger
    def confirm_finish_game(self, game: Game) -> None:
        game.finish()
        for player in game.players:
            self.viewer.view(player.id, constants.GAME_FINISHED, keyboards.get_start_game())

    @logger
    def look_table(self, game: Game, player: Player) -> None:
        table, hints, lives = game.get_table_info()
        output = '{}\n{}: {}\n{}: {}'.format(
            str(table) if table.len() != 0 else constants.EMPTY_TABLE,
            constants.HINTS, str(hints),
            constants.LIVES, str(lives),
        )
        self.viewer.view(player.id, output)

    @logger
    def look_trash(self, game: Game, player: Player) -> None:
        trash = game.get_trash_cards()
        self.viewer.view(player.id, str(trash) if trash.len() != 0 else constants.EMPTY_TRASH)

    @logger
    def look_hands(self, game: Game, player: Player) -> None:
        for p in game.players:
            if p.id != player.id:
                hand = p.get_hand_cards()
                self.viewer.view(
                    player.id,
                    '{}\n{}'.format(p.get_name(), str(hand) if hand.len() != 0 else constants.EMPTY_HAND),
                )

    @logger
    def request_for_move_to_trash(self, player: Player) -> None:
        count_of_cards = player.request_move_to_trash()
        self.viewer.view(player.id, constants.ENTER_CARD_NUMBER, keyboards.get_request_card_number(count_of_cards))

    @logger
    def move_to_trash(self, game: Game, player: Player, card_number: str) -> None:
        trashed_card = game.move_to_trash(player, int(card_number) - 1)
        self.broadcast(
            constants.PLAYER_HAS_TRASHED_CARD.format(player.name, str(trashed_card)),
            game,
            constants.PLAYER_HAS_TRASHED_CARD.format(constants.YOU, str(trashed_card)),
            player.id,
        )
        self.next_turn(game)

    @logger
    def request_for_move_to_table(self, player: Player) -> None:
        count_of_cards = player.request_move_to_table()
        self.viewer.view(player.id, constants.ENTER_CARD_NUMBER, keyboards.get_request_card_number(count_of_cards))

    @logger
    def move_to_table(self, game: Game, player: Player, card_number: str) -> None:
        try:
            success, put_card = game.move_to_table(player, int(card_number) - 1)
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

    @logger
    def broadcast(self, message: str, game: Game, self_message: str = None, player_id: str = None):
        for p in game.players:
            self.viewer.view(p.id, message if player_id is None or player_id != p.id else self_message)

    @logger
    def next_turn(self, game: Game):
        try:
            player_number = game.next_turn()
            self.turn_player(game, player_number)
        except GameIsEnded:
            score = game.get_score()
            self.broadcast(constants.SCORE.format(str(score)), game)
            self.confirm_finish_game(game)

    @logger
    def request_for_hint_recipient(self, game: Game, player: Player) -> None:
        names = [p.get_name() for p in game.players if p.id != player.id]
        if len(names) > 1:
            player.request_hint_recipient()
            self.viewer.view(player.id, constants.ENTER_PLAYER_NAME, keyboards.get_request_player_name(names))
        else:
            self.request_for_type_of_hint(game, player, names[0])

    @logger
    def request_for_type_of_hint(self, game: Game, player: Player, recipient_name: str) -> None:
        recipient_number = 0
        for i, p in enumerate(game.players):
            if p.get_name() == recipient_name:
                recipient_number = i
        player.request_hint_type(recipient_number)
        self.viewer.view(player.id, constants.ENTER_TYPE_OF_HINT, keyboards.get_type_of_hint())

    @logger
    def request_for_hint_color(self, player: Player) -> None:
        player.request_hint_color()
        self.viewer.view(player.id, constants.ENTER_COLOR, keyboards.get_colors())

    @logger
    def request_for_hint_value(self, player: Player) -> None:
        player.request_hint_value()
        self.viewer.view(player.id, constants.ENTER_VALUE, keyboards.get_values())

    @logger
    def hint_color(self, game: Game, player: Player, color: str) -> None:
        recipient_number = player.get_recipient_hint_number()
        card_numbers = game.hint_color(player, recipient_number, color)
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

    @logger
    def hint_value(self, game: Game, player: Player, value: str) -> None:
        recipient_number = player.get_recipient_hint_number()
        card_numbers = game.hint_value(player, recipient_number, value)
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

    @logger
    def broadcast_hint(self, game: Game, player: Player, recipient_number: int,
                       hint: str, common_hint: str, self_hint: str):
        for i, p in enumerate(game.players):
            if i == recipient_number:
                self.viewer.view(p.id, hint)
            elif p.id == player.id:
                self.viewer.view(p.id, self_hint)
            else:
                self.viewer.view(p.id, common_hint)

    @logger
    def goto_menu(self, game: Game, player: Player):
        player.set_playing_state()
        self.viewer.view(player.id, constants.YOUR_TURN, keyboards.get_turn(game.hints > 0))

    @logger
    def operate(self, player_id: str, player_name: str, text: str):
        player = Player(player_id, self.database)
        player.set_name(player_name)
        game_id = player.get_game_id()

        if game_id is None or game_id == 'None':
            if text == constants.CREATE_GAME and player.is_not_playing():
                self.create_new_game(player)
            elif text == constants.CONNECT_TO_GAME and player.is_not_playing():
                self.request_id_for_connect_to_game(player)
            elif text == constants.DONT_CONNECT_TO_GAME and player.is_request_game_code_to_connect():
                self.reject_connect_to_game(player)
            else:
                if player.is_request_game_code_to_connect():
                    self.connect_to_game(player, text)
            player.save()
        else:
            game = Game()
            game.set_id(game_id)
            game.set_database(self.database)
            game.load()
            if text == constants.FINISH_GAME:
                self.request_for_confirm_finish_game(player)
            elif text == constants.YES_FINISH_GAME:
                self.confirm_finish_game(game)
                return
            elif text == constants.NO_CONTINUE_GAME:
                self.reject_finish_game(game, player)
            elif text == constants.START_GAME:
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
                self.request_for_move_to_trash(player)
            elif text == constants.PUT:
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
                    self.move_to_trash(game, player, text)
                elif player.is_request_card_number_to_put():
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

            if not game.deleted:
                game.save()
                player.save()

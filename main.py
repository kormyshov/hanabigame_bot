import os
import telebot
import logging

import keyboards
import constants
from player import Player
from game import Game

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))


@bot.message_handler(commands=['start'])
def start_message(message):
    # database.create_database()
    bot.send_message(message.chat.id, constants.ONBOARDING, reply_markup=keyboards.get_start_game())


def create_new_game(player: Player) -> None:
    logger = logging.getLogger('hanabigame.main.create_new_game')
    logger.info('start')
    game_id = Game('').init_game(player)
    logger.info('init game with game_id = ' + game_id)
    bot.send_message(player.id, constants.GAME_CREATED)
    bot.send_message(player.id, game_id, reply_markup=keyboards.get_waiting_second_player())


def request_id_for_connect_to_game(player):
    print('into def')
    player.request_game_code_to_connect()
    print('before send')
    bot.send_message(player.id, constants.ENTER_GAME_CODE_TO_CONNECT)


def connect_to_game(player, game_id):
    logger = logging.getLogger('hanabigame.main.connect_to_game')
    logger.info('start with game_id = ' + game_id)
    game = Game(game_id)
    logger.info('get game')
    response, players = game.connect_player(player)
    logger.info('get reponse ' + str(response))
    if response == Game.ConnectResponse.ERROR:
        bot.send_message(player.id, constants.THERE_IS_NO_GAME_WITH_THIS_CODE, reply_markup=keyboards.start_game)
    else:
        print('into else ' + str(len(players)))
        for p in players[:-1]:
            bot.send_message(p.id, constants.PLAYER_CONNECT_TO_GAME.format(player.name),
                             reply_markup=keyboards.waiting_start_game)
        bot.send_message(player.id, constants.YOU_HAS_BEEN_CONNECTED_TO_GAME, reply_markup=keyboards.waiting_start_game)
        if response == Game.ConnectResponse.OK_AND_START:
            start_game(game)


def start_game(game):
    print('in start_game')
    players = game.start()
    print('started game and get players')
    for i, p in enumerate(players):
        bot.send_message(p.id, constants.GAME_STARTED)
    print('output GAME_STARTED message')
    turn_player(players, 0)
    print('end start_game')


def turn_player(players, num):
    print('in turn_player')
    for i, p in enumerate(players):
        print('if with ' + str(i) + ' and ' + str(num))
        if i == num:
            bot.send_message(p.id, constants.YOUR_TURN, reply_markup=keyboards.turn)
        else:
            print(str(p.id))
            print('len = ' + str(len(players)))
            print(str(players))
            print(str(players[1]))
            print(str(players[1].id))
            print(players[1].get_name())
            bot.send_message(p.id, constants.TURN_ANOTHER_PLAYER.format(players[num].get_name()),
                             reply_markup=keyboards.waiting_turn)
    print('end turn_player')


def request_for_confirm_finish_game(player: Player) -> None:
    logger = logging.getLogger('hanabigame.main.request_for_confirm_finish_game')
    logger.info('start')
    player.confirm_finish_game()
    logger.info('player confirmed')
    bot.send_message(player.id, constants.ARE_YOU_SURE, reply_markup=keyboards.get_confirm_finish_game())


def reject_finish_game(player):
    logger = logging.getLogger('hanabigame.main.reject_finish_game')
    logger.info('start')
    player.reject_finish_game()
    logger.info('player rejected finishing')
    # TODO: добавить выбор клавиатуры в зависимости от state
    bot.send_message(player.id, constants.LETS_CONTINUE, reply_markup=keyboards.get_waiting_second_player())


def confirm_finish_game() -> None:
    logger = logging.getLogger('hanabigame.main.confirm_finish_game')
    logger.info('start')
    Game('').finish()
    logger.info('game finished')
    for player in Game('').players:
        bot.send_message(player.id, constants.GAME_FINISHED, reply_markup=keyboards.get_start_game())


def look_table(player, game):
    table_str, hints, lives = game.get_table_output()
    output = table_str if table_str != '' else constants.EMPTY_TABLE
    output += '\n' + constants.HINTS + ': ' + str(hints)
    output += '\n' + constants.LIVES + ': ' + str(lives)
    bot.send_message(player.id, output)


def look_trash(player, game):
    trash_str = game.get_trash_output()
    bot.send_message(player.id, trash_str if trash_str != '' else constants.EMPTY_TRASH)


def look_hands(player, game):
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
            bot.send_message(player.id, p.get_name() + '\n' + hand_str if hand_str != '' else constants.EMPTY_HAND)


def request_for_move_to_trash(player):
    logger = logging.getLogger('hanabigame.main.request_for_move_to_trash')
    logger.info('start')
    count_of_cards = player.request_move_to_trash()
    logger.info('got count_of_cards')
    bot.send_message(player.id, constants.ENTER_CARD_NUMBER,
                     reply_markup=keyboards.get_request_card_number(count_of_cards))


def move_to_trash(player, game, card_number_str):
    logger = logging.getLogger('hanabigame.main.move_to_trash')
    logger.info('start')
    trashed_card = player.move_to_trash(int(card_number_str) - 1)
    logger.info('moved to trash and got trashed crad')
    for p in game.players:
        logger.info('get player')
        bot.send_message(p.id,
                         constants.PLAYER_HAS_TRASHED_CARD.format((player.name if player.id != p.id else constants.YOU),
                                                                  trashed_card))

    player_number = game.next_turn()
    logger.info('next turn')
    turn_player(game.players, int(player_number))


def request_for_move_to_table(player):
    logger = logging.getLogger('hanabigame.main.request_for_move_to_table')
    logger.info('start')
    count_of_cards = player.request_move_to_table()
    logger.info('got count_of_cards')
    bot.send_message(player.id, constants.ENTER_CARD_NUMBER,
                     reply_markup=keyboards.get_request_card_number(count_of_cards))


def move_to_table(player, game, card_number_str):
    logger = logging.getLogger('hanabigame.main.move_to_table')
    logger.info('start')
    put_card, success = player.move_to_table(int(card_number_str) - 1)
    logger.info('moved to table and got put card')
    for p in game.players:
        logger.info('get player')
        if success:
            bot.send_message(p.id,
                             constants.PLAYER_HAS_PUT_CARD.format((player.name if player.id != p.id else constants.YOU),
                                                                  put_card))
        else:
            bot.send_message(p.id, constants.PLAYER_TRIED_TO_PUT_CARD.format(
                (player.name if player.id != p.id else constants.YOU), put_card))

    player_number = game.next_turn()
    logger.info('next turn')
    turn_player(game.players, int(player_number))


def request_for_hint_recipient(player, game):
    logger = logging.getLogger('hanabigame.main.request_for_hint_recipient')
    logger.info('start')
    game.load()
    names = [p.get_name() for p in game.players if p.id != player.id]
    logger.info('get names ' + ', '.join(names))
    if len(names) > 1:
        logger.info('many players')
        player.request_hint_recipient()
        bot.send_message(player.id, constants.ENTER_PLAYER_NAME, reply_markup=keyboards.get_request_player_name(names))
    else:
        request_for_type_of_hint(player, game, names[0])


def request_for_type_of_hint(player, game, recipient_name):
    logger = logging.getLogger('hanabigame.main.request_for_type_of_hint')
    logger.info('start')
    game.load()
    recipient_number = 0
    for i, p in enumerate(game.players):
        if p.get_name() == recipient_name:
            recipient_number = i
    player.request_hint_type(recipient_number)
    logger.info('switch player state')
    bot.send_message(player.id, constants.ENTER_TYPE_OF_HINT, reply_markup=keyboards.type_of_hint)


def request_for_hint_color(player):
    logger = logging.getLogger('hanabigame.main.request_for_hint_color')
    logger.info('start')
    player.request_hint_color()
    logger.info('switch player state')
    bot.send_message(player.id, constants.ENTER_COLOR, reply_markup=keyboards.colors)


def request_for_hint_value(player):
    logger = logging.getLogger('hanabigame.main.request_for_hint_value')
    logger.info('start')
    player.request_hint_value()
    logger.info('switch player state')
    bot.send_message(player.id, constants.ENTER_VALUE, reply_markup=keyboards.values)


def hint_color(player, game, color):
    logger = logging.getLogger('hanabigame.main.hint_color')
    logger.info('start')
    recipient_number = player.get_recipient_hint_number()
    logger.info('get recipient number = ' + str(recipient_number) + ' with type ' + str(type(recipient_number)))
    game.load()
    card_numbers = game.hint_color(recipient_number, color)
    logger.info('get card numbers ' + ','.join(map(str, card_numbers)))
    for i, p in enumerate(game.players):
        if i == recipient_number:
            bot.send_message(p.id, constants.PLAYER_HINT_COLOR_TO_YOU.format(player.get_name(), color,
                                                                             ', '.join(map(str, card_numbers))))
        elif p.id == player.id:
            bot.send_message(p.id, constants.YOU_HAS_HINT.format(game.players[recipient_number].get_name()))
        else:
            bot.send_message(p.id, constants.PLAYER_HINT_COLOR_TO_OTHER.format(player.get_name(), game.players[
                recipient_number].get_name(), color, ', '.join(map(str, card_numbers))))

    player_number = game.next_turn()
    logger.info('next turn')
    turn_player(game.players, int(player_number))


def hint_value(player, game, value):
    logger = logging.getLogger('hanabigame.main.hint_value')
    logger.info('start')
    recipient_number = player.get_recipient_hint_number()
    logger.info('get recipient number = ' + str(recipient_number) + ' with type ' + str(type(recipient_number)))
    game.load()
    card_numbers = game.hint_value(recipient_number, value)
    logger.info('get card numbers ' + ','.join(map(str, card_numbers)))
    for i, p in enumerate(game.players):
        if i == recipient_number:
            bot.send_message(p.id, constants.PLAYER_HINT_VALUE_TO_YOU.format(player.get_name(), value,
                                                                             ', '.join(map(str, card_numbers))))
        elif p.id == player.id:
            bot.send_message(p.id, constants.YOU_HAS_HINT.format(game.players[recipient_number].get_name()))
        else:
            bot.send_message(p.id, constants.PLAYER_HINT_VALUE_TO_OTHER.format(player.get_name(), game.players[
                recipient_number].get_name(), value, ', '.join(map(str, card_numbers))))

    player_number = game.next_turn()
    logger.info('next turn')
    turn_player(game.players, int(player_number))


@bot.message_handler(content_types='text')
def message_reply(message):
    logger = logging.getLogger('hanabigame.main.message_reply')
    logger.info('start with message.text = ' + message.text)
    player = Player(str(message.chat.id))
    logger.info('get Player')
    player.set_name(message.from_user.first_name)
    logger.info('set player name')
    game_id = player.get_game_id()
    logger.info('get game id = ' + str(game_id))

    if game_id is None or game_id == 'None':
        logger.info('in if with game_id is None')
        if message.text == constants.CREATE_GAME:
            logger.info('branch create_new_game')
            create_new_game(player)
        elif message.text == constants.CONNECT_TO_GAME:
            request_id_for_connect_to_game(player)
        else:
            if player.is_request_game_code_to_connect():
                connect_to_game(player, message.text)
    else:
        logger.info('in if with game_id is not None')
        Game(game_id).load()
        if message.text == constants.FINISH_GAME:
            logger.info('branch request_for_confirm_finish_game')
            request_for_confirm_finish_game(player)
        elif message.text == constants.YES_FINISH_GAME:
            logger.info('branch confirm_finish_game')
            confirm_finish_game()
        elif message.text == constants.NO_CONTINUE_GAME:
            logger.info('branch reject_finish_game')
            reject_finish_game(player)
        elif message.text == constants.START_GAME:
            start_game()
        elif message.text == constants.LOOK_TABLE:
            look_table(player)
        elif message.text == constants.LOOK_TRASH:
            look_trash(player)
        elif message.text == constants.LOOK_HANDS:
            look_hands(player)
        elif message.text == constants.TRASH:
            request_for_move_to_trash(player)
        elif message.text == constants.PUT:
            request_for_move_to_table(player)
        elif message.text == constants.HINT:
            request_for_hint_recipient(player)
        elif message.text == constants.COLOR:
            request_for_hint_color(player)
        elif message.text == constants.VALUE:
            request_for_hint_value(player)
        else:
            if player.is_request_card_number_to_trash():
                move_to_trash(player, message.text)
            if player.is_request_card_number_to_put():
                move_to_table(player, message.text)
            if player.is_request_hint_recipient():
                request_for_type_of_hint(player, message.text)
            if player.is_request_hint_color():
                hint_color(player, message.text)
            if player.is_request_hint_value():
                hint_value(player, message.text)

        Game(game_id).save()

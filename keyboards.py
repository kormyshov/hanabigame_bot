from telebot import types
import buttons

start_game = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_game.add(buttons.create_game)
start_game.add(buttons.connect_game)

waiting_second_player = types.ReplyKeyboardMarkup(resize_keyboard=True)
waiting_second_player.add(buttons.finish_game)

confirm_finish_game = types.ReplyKeyboardMarkup(resize_keyboard=True)
confirm_finish_game.add(buttons.yes_finish_game)
confirm_finish_game.add(buttons.no_continue_game)

waiting_start_game = types.ReplyKeyboardMarkup(resize_keyboard=True)
waiting_start_game.add(buttons.start_game)
waiting_start_game.add(buttons.finish_game)

waiting_turn = types.ReplyKeyboardMarkup(resize_keyboard=True)
waiting_turn.add(buttons.look_hands)
waiting_turn.add(buttons.look_table)
waiting_turn.add(buttons.look_trash)
waiting_turn.add(buttons.finish_game)

turn = types.ReplyKeyboardMarkup(resize_keyboard=True)
turn.add(buttons.put)
turn.add(buttons.trash)
turn.add(buttons.hint)
turn.add(buttons.look_hands)
turn.add(buttons.look_table)
turn.add(buttons.look_trash)
turn.add(buttons.finish_game)

type_of_hint = types.ReplyKeyboardMarkup(resize_keyboard=True)
type_of_hint.add(buttons.color)
type_of_hint.add(buttons.value)
type_of_hint.add(buttons.back)

colors = types.ReplyKeyboardMarkup(resize_keyboard=True)
colors.add(buttons.green)
colors.add(buttons.red)
colors.add(buttons.blue)
colors.add(buttons.yellow)
colors.add(buttons.white)
colors.add(buttons.back)

values = types.ReplyKeyboardMarkup(resize_keyboard=True)
values.add(buttons.one)
values.add(buttons.two)
values.add(buttons.three)
values.add(buttons.four)
values.add(buttons.five)
values.add(buttons.back)


def get_request_card_number(count_of_cards):
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, count_of_cards + 1):
        k.add(buttons.get_card_number(i))
    k.add(buttons.back)
    return k


def get_request_player_name(names):
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in names:
        k.add(buttons.get_player_name(name))
    k.add(buttons.back)
    return k

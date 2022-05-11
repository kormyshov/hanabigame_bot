from telebot import types
import constants

create_game = types.KeyboardButton(constants.CREATE_GAME)
connect_game = types.KeyboardButton(constants.CONNECT_TO_GAME)
finish_game = types.KeyboardButton(constants.FINISH_GAME)
start_game = types.KeyboardButton(constants.START_GAME)

yes_finish_game = types.KeyboardButton(constants.YES_FINISH_GAME)
no_continue_game = types.KeyboardButton(constants.NO_CONTINUE_GAME)

look_hands = types.KeyboardButton(constants.LOOK_HANDS)
look_table = types.KeyboardButton(constants.LOOK_TABLE)
look_trash = types.KeyboardButton(constants.LOOK_TRASH)

put = types.KeyboardButton(constants.PUT)
trash = types.KeyboardButton(constants.TRASH)
hint = types.KeyboardButton(constants.HINT)

back = types.KeyboardButton(constants.BACK)

color = types.KeyboardButton(constants.COLOR)
value = types.KeyboardButton(constants.VALUE)

green = types.KeyboardButton(constants.GREEN)
red = types.KeyboardButton(constants.RED)
blue = types.KeyboardButton(constants.BLUE)
yellow = types.KeyboardButton(constants.YELLOW)
white = types.KeyboardButton(constants.WHITE)

one = types.KeyboardButton(constants.ONE)
two = types.KeyboardButton(constants.TWO)
three = types.KeyboardButton(constants.THREE)
four = types.KeyboardButton(constants.FOUR)
five = types.KeyboardButton(constants.FIVE)


def get_card_number(number):
    return types.KeyboardButton(str(number))


def get_player_name(name):
    return types.KeyboardButton(name)

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from typing import List
import constants


def get_start_game() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.CREATE_GAME))
    keyboard.add(KeyboardButton(constants.CONNECT_TO_GAME))
    return keyboard


def get_waiting_second_player() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.FINISH_GAME))
    return keyboard


def get_confirm_finish_game() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.YES_FINISH_GAME))
    keyboard.add(KeyboardButton(constants.NO_CONTINUE_GAME))
    return keyboard


def get_waiting_start_game() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.START_GAME))
    keyboard.add(KeyboardButton(constants.FINISH_GAME))
    return keyboard


def get_waiting_turn() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.LOOK_HANDS))
    keyboard.add(KeyboardButton(constants.LOOK_TABLE))
    keyboard.add(KeyboardButton(constants.LOOK_TRASH))
    keyboard.add(KeyboardButton(constants.FINISH_GAME))
    return keyboard


def get_turn() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.PUT))
    keyboard.add(KeyboardButton(constants.TRASH))
    keyboard.add(KeyboardButton(constants.HINT))
    keyboard.add(KeyboardButton(constants.LOOK_HANDS))
    keyboard.add(KeyboardButton(constants.LOOK_TABLE))
    keyboard.add(KeyboardButton(constants.LOOK_TRASH))
    keyboard.add(KeyboardButton(constants.FINISH_GAME))
    return keyboard


def get_type_of_hint() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.COLOR))
    keyboard.add(KeyboardButton(constants.VALUE))
    keyboard.add(KeyboardButton(constants.BACK))
    return keyboard


def get_colors() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.GREEN))
    keyboard.add(KeyboardButton(constants.RED))
    keyboard.add(KeyboardButton(constants.BLUE))
    keyboard.add(KeyboardButton(constants.YELLOW))
    keyboard.add(KeyboardButton(constants.WHITE))
    keyboard.add(KeyboardButton(constants.BACK))
    return keyboard


def get_values() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(constants.ONE))
    keyboard.add(KeyboardButton(constants.TWO))
    keyboard.add(KeyboardButton(constants.THREE))
    keyboard.add(KeyboardButton(constants.FOUR))
    keyboard.add(KeyboardButton(constants.FIVE))
    keyboard.add(KeyboardButton(constants.BACK))
    return keyboard


def get_request_card_number(count_of_cards: int) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, count_of_cards + 1):
        keyboard.add(KeyboardButton(str(i)))
    keyboard.add(KeyboardButton(constants.BACK))
    return keyboard


def get_request_player_name(names: List[str]) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in names:
        keyboard.add(KeyboardButton(name))
    keyboard.add(KeyboardButton(constants.BACK))
    return keyboard

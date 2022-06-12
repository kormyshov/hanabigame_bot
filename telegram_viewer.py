import os
import telebot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from abstract_viewer import AbstractViewer, Iterable, Optional


bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))


class TelegramViewer(AbstractViewer):
    def __init__(self):
        pass

    def view(self, player_id: str, message: str, keyboard: Optional[Iterable[str]] = None) -> None:
        if keyboard is not None:
            bot.send_message(player_id, message, reply_markup=self.get_keyboard(keyboard))
        else:
            bot.send_message(player_id, message)

    def get_keyboard(self, actions: Iterable[str]) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for action in actions:
            keyboard.add(KeyboardButton(action))
        return keyboard

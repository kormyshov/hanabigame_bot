import os
import telebot

import keyboards
import constants
from database import Database
from controller import controller

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))


@bot.message_handler(commands=['start'])
def start_message(message):
    # db.create_tables()
    bot.send_message(message.chat.id, constants.ONBOARDING, reply_markup=keyboards.get_start_game())


@bot.message_handler(content_types='text')
def message_reply(message):
    db = Database()
    controller(str(message.chat.id), message.from_user.first_name, message.text, db)

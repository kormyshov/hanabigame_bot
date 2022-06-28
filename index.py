import telebot
import logging
from main import bot


def handler(event, _):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Program started')

    message = telebot.types.Update.de_json(event['body'])
    bot.process_new_updates([message])
    return {
        'statusCode': 200,
        'body': '!',
    }

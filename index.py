import telebot
import logging
from main import bot


def handler(event, _):
    logging.getLogger().setLevel(logging.INFO)
    root_handler = logging.getLogger().handlers[0]
    root_handler.setFormatter(logging.Formatter(
        '[%(levelname)s]\t%(request_id)s\t%(name)s\t%(message)s\n'
    ))
    logging.info('Program started')

    message = telebot.types.Update.de_json(event['body'])
    bot.process_new_updates([message])
    return {
        'statusCode': 200,
        'body': '!',
    }

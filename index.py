import telebot
import logging
import sys
from main import bot


def handler(event, _):
    logger = logging.getLogger('hanabigame')
    logger.setLevel(logging.INFO)

    fh = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    logger.info('Program started')

    message = telebot.types.Update.de_json(event['body'])
    bot.process_new_updates([message])
    return {
        'statusCode': 200,
        'body': '!',
    }

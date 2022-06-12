import keyboards
import constants
from database import Database
from controller import Controller
from telegram_viewer import TelegramViewer, bot


@bot.message_handler(commands=['start'])
def start_message(message):
    # db.create_tables()
    TelegramViewer().view(message.chat.id, constants.ONBOARDING, keyboards.get_start_game())


@bot.message_handler(content_types='text')
def message_reply(message):
    db = Database()
    viewer = TelegramViewer()
    Controller(db, viewer).operate(str(message.chat.id), message.from_user.first_name, message.text)

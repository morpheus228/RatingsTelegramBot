import telebot
from database.database import Database

telebot.apihelper.ENABLE_MIDDLEWARE = True

with open('telegram_token.txt', 'r') as file:
    telegram_token = file.readline().strip()

bot = telebot.TeleBot(telegram_token)
db = Database()
db_bot = db.DBBot(bot)




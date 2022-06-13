from views import *
from config import *

from spaces import create, enter, mine
from checking import check_new_user


@bot.message_handler(func=lambda m: m.text in ['/start', '/help', 'Главное меню 🔙'])
def menu(message):
    bot.send_message(message.from_user.id, text='Выбирай, что сделать хочешь...', reply_markup=router_markup)


@bot.message_handler(func=lambda m: m.text == 'Мои комнаты 👇')
def my_spaces_start(message):
    mine.start(message)


@bot.message_handler(func=lambda m: m.text == 'Зайти в комнату 🔘')
def enter_space_start(message):
    enter.start(message)


@bot.message_handler(func=lambda m: m.text == 'Создать комнату 🔨')
def create_space_start(message):
    create.start(message)


def error(message):
    bot.send_message(message.from_user.id, 'Ошибка...')
    menu(message)


if __name__ == '__main__':
    bot.infinity_polling()
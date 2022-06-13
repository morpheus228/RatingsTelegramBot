from config import *
from valid_space.views import *
from valid_space import choices, top, viewing, exiting
from valid_space.adding import adding
from checking import *


def enter(message_or_call, space, which):
    if which == 'my':
        call = message_or_call
        bot.edit_message_text(text=f'Ты в комнате "{space.name}"', chat_id=call.message.chat.id,
                              message_id=call.message.id)
    elif which == 'not_my':
        message = message_or_call
        bot.send_message(message.from_user.id, f'Ты в комнате "{space.name}"')

    db.alter_user_current_space(message_or_call.from_user.id, space.id)
    send_router(message_or_call, space)


def send_router(message, space):
    space_router_markup = get_space_router_markup(message.from_user.id, space)
    bot.send_message(message.from_user.id, f'Выбирай, что сделать хочешь...', reply_markup=space_router_markup)


@bot.message_handler(func=lambda m: m.text == 'Начать сравнения ▶')
def choices_start(message):
    if db.get_user_current_space_id(message.from_user.id) is not None:
        choices.start(message)


@bot.message_handler(func=lambda m: m.text == 'Топ 🔝')
def top_start(message):
    if db.get_user_current_space_id(message.from_user.id) is not None:
        top.start(message.from_user.id)


@bot.message_handler(func=lambda m: m.text == 'Список объектов 👇')
def viewing_start(message):
    if db.get_user_current_space_id(message.from_user.id) is not None:
        viewing.start(message.from_user.id)


@bot.message_handler(func=lambda m: m.text == 'Добавить объекты 🔨')
def adding_start(message):
    if db.get_user_current_space_id(message.from_user.id) is not None:
        adding.start(message)


@bot.message_handler(func=lambda m: m.text == 'Выйти из комнаты 🚶')
def exiting_start(message):
    if db.get_user_current_space_id(message.from_user.id) is not None:
        exiting.start(message)


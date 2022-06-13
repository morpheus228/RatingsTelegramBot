from spaces.views import *
from config import *


def start(message, user_id=None):
    if user_id is not None:
        my_spaces_keyboard = create_my_spaces_keyboard(user_id)
    else:
        my_spaces_keyboard = create_my_spaces_keyboard(message.from_user.id)

    if len(my_spaces_keyboard.keyboard) == 0:
        bot.send_message(message.chat.id, "😥 У тебя нет ни одной комнаты", reply_markup=my_spaces_keyboard)
    else:
        bot.send_message(message.chat.id, "📋 Твои комнаты:", reply_markup=my_spaces_keyboard)


@bot.callback_query_handler(func=lambda call: call.message.text=='📋 Твои комнаты:')
def my_spaces_router(call):
    text = space_view(call.data)
    bot.edit_message_text(text=text, chat_id=call.message.chat.id, parse_mode='Markdown',
                          message_id=call.message.id, reply_markup=space_editor_keyboard)


@bot.callback_query_handler(func=lambda call: call.message.text.__contains__('Название:'))
def space_router(call):
    if call.data == 'delete':
        delete_space(call)
    elif call.data == 'back':
        back(call)


def back(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    start(call.message, user_id=call.from_user.id)


def delete_space(call):
    text = call.message.text
    space_id = int(list(list(text.split('ID: '))[1].split('Приватный:'))[0])
    db.delete_space_by_id(space_id)
    back(call)
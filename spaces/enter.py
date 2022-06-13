from spaces.views import *
from views import *
from config import *
from valid_space.router import enter


def start(message):
    bot.send_message(message.from_user.id, 'В какую комнату ты хочешь зайти?', reply_markup=which_space_enter_markup)


@bot.callback_query_handler(func=lambda call: call.message.text == 'В какую комнату ты хочешь зайти?')
def take_which_space(call):
    if call.data == 'not_my':
        enter_not_my_space(call)
    elif call.data == 'my':
        enter_my_space(call)


############################################################################################################
def enter_my_space(call):
    my_spaces_keyboard = create_my_spaces_keyboard(call.from_user.id)
    if len(my_spaces_keyboard.keyboard) == 0:
        bot.edit_message_text(text="😥 У тебя нет ни одной комнаты", chat_id=call.message.chat.id,
                     message_id=call.message.id)
    else:
        bot.edit_message_text(text='Выберите комнату...', chat_id=call.message.chat.id,
                     message_id=call.message.id, reply_markup=my_spaces_keyboard)


@bot.callback_query_handler(func=lambda call: call.message.text == 'Выберите комнату...')
def take_my_space(call):
    space = db.get_space_by_id(call.data)
    enter(call, space, 'my')


############################################################################################################
def enter_not_my_space(call):
    bot.edit_message_text(text='Введите ID комнаты...', chat_id=call.message.chat.id,
                     message_id=call.message.id)
    bot.register_next_step_handler(call.message, take_space_id)


def take_space_id(message):
    if int(message.text) in db.get_all_space_features('id'):
        space = db.get_space_by_id(message.text)
        if space.private:
            bot.send_message(message.from_user.id, 'Введите пароль от комнаты...')
            bot.register_next_step_handler(message, take_space_password, space=space)
        else:
            enter(message, space, 'not_my')
    else:
        bot.send_message(message.from_user.id, '😥 Такой комнаты не существует')


def take_space_password(message, space):
    if message.text == space.password:
        enter(message, space, 'not_my')
    else:
        bot.send_message(message.from_user.id, '😥 Пароль неверный')
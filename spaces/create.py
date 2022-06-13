from spaces.views import *
from views import *
from config import *
import main


def start(message):
    status = db.check_spaces_number_limit(message.from_user.id)
    if status:
        bot.send_message(message.from_user.id, 'Выберите ТИП комнаты...', reply_markup=space_type_markup)
    else:
        bot.send_message(message.from_user.id, f'Превышен лимит по количеству комнат ({db.spaces_number_limit} штук).')


@bot.callback_query_handler(func=lambda call: call.message.text == 'Выберите ТИП комнаты...')
def take_space_type(call):
    space = db.Space(creator=call.from_user.id)
    space.private = True if call.data == 'private' else False

    bot.edit_message_text(text='Введите НАЗВАНИЕ комнаты...', chat_id=call.message.chat.id,
                          message_id=call.message.id)
    bot.register_next_step_handler(call.message, take_space_name, space=space)


def take_space_name(message, space):
    if len(message.text) > 30:
        bot.send_message(message.from_user.id, 'Слишком длинное название')
        bot.send_message(message.from_user.id, 'Название не может быть длинее 30 символов...')
        start(message)

    else:
        space.name = message.text

        if space.private:
            bot.send_message(message.from_user.id, 'Введите ПАРОЛЬ для комнаты...')
            bot.register_next_step_handler(message, take_space_password, space=space)
        else:
            create_space(message, space)


def take_space_password(message, space):
    if len(message.text) > 30:
        bot.send_message(message.from_user.id, 'Слишком длинный пароль.')
        bot.send_message(message.from_user.id, 'Пароль не может быть длинее 30 символов.')
        message.text = 'Приватная'
        take_space_type(message, space)

    else:
        space.password = message.text
        create_space(message, space)


def create_space(message, space):
    space.save()
    bot.send_message(message.from_user.id, f'Комната "{space.name}" успешно создана ✅')
    main.menu(message)





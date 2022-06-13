from valid_space.adding.vk.parser import vk_user_parser
from valid_space.views import *
from valid_space.adding.views import *
from checking import check_space_validity
from valid_space import router
from valid_space.adding.vk.views import messages_according_adding_status

users_data = {}


@bot.callback_query_handler(func=lambda call: call.verified and
    (call.message.text == 'Выберите ИСТОЧНИК...') and (call.data == 'vk_user'))
def vk_group_adding(call):
    db_bot.edit_callback_message(text='Введите ID страницы...', message=call.message, delete=True)
    bot.register_next_step_handler(call.message, take_vk_user_id)


def take_vk_user_id(message):
    vk_user_id = message.text if not message.text.isnumeric() else int(message.text)
    vk_user_id = vk_user_parser.check_existence(vk_user_id)

    if not vk_user_id:
        bot.send_message(message.from_user.id, '😥 Страницы с таким ID не существует')
    else:
        space_id = db.get_user_current_space_id(message.from_user.id)
        users_data[message.from_user.id] = {'vk_user_id': vk_user_id, 'space_id': space_id}
        bot.send_message(message.from_user.id, 'Введите ОПИСАНИЕ объекта...', reply_markup=no_description_markup)
        bot.register_next_step_handler(message, take_object_description, vk_user_id=vk_user_id)


def take_object_description(message, vk_user_id):
    if len(message.text) > 50:
        bot.send_message(message.from_user.id, 'Слишком длинное описание. Оно не может быть длинее 50 символов...')
        bot.send_message(message.from_user.id, 'Введите описание объекта...', reply_markup=no_description_markup)
        bot.register_next_step_handler(message, take_object_description, vk_user_id=vk_user_id)
    else:
        if message.text == no_description_markup_btn1.text:
            description = ''
        else:
            description = message.text

        users_data[message.from_user.id]['description'] = description
        db_bot.send_callback_message(message.from_user.id, 'Какие ФОТОГРАФИИ брать со страницы?',
                                     reply_markup=photo_selector_markup,
                                     space_id=users_data[message.from_user.id]['space_id'])


@bot.callback_query_handler(func=lambda call: call.message.text == 'Какие ФОТОГРАФИИ брать со страницы?')
def take_photo_selector(call):
    user_id = call.from_user.id
    user_data = users_data[user_id]
    vk_user_id = user_data['vk_user_id']
    description = user_data['description']
    space_id = user_data['space_id']
    status, object = vk_user_parser.add_object(vk_user_id, user_id, space_id, description, call.data)

    db_bot.delete_callback_message(call.message)
    bot.send_message(user_id, messages_according_adding_status[status](object.name))
    router.send_router(call, db.get_space_by_id(space_id))

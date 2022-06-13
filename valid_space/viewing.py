from valid_space.views import *
from valid_space import top
from config import db_bot

users_data = {}


def start(user_id):
    space = db.get_space_by_id(db.get_user_current_space_id(user_id))
    users_data[user_id] = {}
    space_objects_keyboard = get_space_objects_keyboard(space.id)

    if len(space_objects_keyboard.keyboard) > 0:
        db_bot.send_callback_message(user_id, f'📋 Объекты комнаты {space.name}:',
                                     reply_markup=space_objects_keyboard, space_id=space.id)
    else:
        bot.send_message(user_id, f'😥 В комнате "{space.name}" нет ни одного объекта')


@bot.callback_query_handler(func=lambda call: call.verified and (
        (call.message.text.__contains__('📋 Объекты комнаты')) or (call.message.text.__contains__('Топ 10 объектов'))))
def my_spaces_router(call):
    if call.message.text.__contains__('📋 Объекты комнаты'):
        users_data[call.from_user.id]['link'] = 'viewing'
    elif call.message.text.__contains__('Топ 10 объектов'):
        users_data[call.from_user.id] = {'link': 'top'}

    object = db.get_object_by_id(call.data)
    text, photo_list = object_view(object)

    db_bot.delete_callback_message(call.message)

    if len(photo_list) > 0:
        photo_messages = bot.send_media_group(call.from_user.id, photo_list)
    else:
        photo_messages = [bot.send_message(call.from_user.id, 'Фотографий у объекта нет')]

    db_bot.send_callback_message(call.from_user.id, text, reply_markup=object_editor_keyboard,
                                 space_id=object.space, related_messages=photo_messages, parse_mode='Markdown')

    users_data[call.from_user.id]['object_id'] = call.data


@bot.callback_query_handler(func=lambda call: call.verified and (
        call.message.text.__contains__('Имя:') and call.data in ['delete', 'back']))
def objects_router(call):
    object_id = users_data[call.from_user.id]['object_id']
    users_data[call.from_user.id]['space_id'] = db.get_object_by_id(object_id).space

    if call.data == 'delete':
        delete_object(call, object_id)
    elif call.data == 'back':
        back(call)


def back(call):
    db_bot.delete_callback_message(call.message)

    if users_data[call.from_user.id]['link'] == 'viewing':
        start(call.from_user.id)

    elif users_data[call.from_user.id]['link'] == 'top':
        top.start(call.from_user.id)


def delete_object(call, object_id):
    db.delete_object_from_space_by_id(object_id)
    back(call)

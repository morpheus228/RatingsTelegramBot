from config import *
from valid_space.adding.photo_iteractions import get_object_photos_dir
from checking import check_space_validity
from valid_space.adding.views import *
from valid_space.views import get_space_router_markup


@bot.callback_query_handler(func=lambda call: call.verified and
    (call.message.text == 'Выберите ИСТОЧНИК...') and (call.data == 'manually'))
def manually_adding(call):
    object = db.Object(space=db.get_user_current_space_id(call.from_user.id), photos=[],
                        source='manually', creator=call.from_user.id)

    db_bot.edit_callback_message(text='Введите ИМЯ объекта...', message=call.message, delete=True)
    bot.register_next_step_handler(call.message, take_object_name, object=object)


def take_object_name(message, object):
    if len(message.text) > 30:
        bot.send_message(message.from_user.id, 'Слишком длинное имя. Оно не может быть длинее 30 символов...')
        bot.send_message(message.from_user.id, 'Введите ИМЯ объекта...')
        bot.register_next_step_handler(message, take_object_name, object=object)
    else:
        object.name = message.text
        bot.send_message(message.from_user.id, 'Введите ОПИСАНИЕ объекта...', reply_markup=no_description_markup)
        bot.register_next_step_handler(message, take_object_description, object)


def take_object_description(message, object):
    if len(message.text) > 50:
        bot.send_message(message.from_user.id, 'Слишком длинное описание. Оно не может быть длинее 50 символов...')
        bot.send_message(message.from_user.id, 'Введите ОПИСАНИЕ объекта...', reply_markup=no_description_markup)
        bot.register_next_step_handler(message, take_object_description, object)
    else:
        if message.text == no_description_markup_btn1.text:
            object.description = ''
        else:
            object.description = message.text

        bot.send_message(message.from_user.id, 'Отправьте ФОТОГРАФИЮ объекта...', reply_markup=no_photo_markup)
        bot.register_next_step_handler(message, take_object_photos, object)


def take_object_photos(message, object):
    object.save()
    if message.photo is not None:
        photo_id = message.photo[-1].file_id
        photo_info = bot.get_file(photo_id)
        down_file = bot.download_file(photo_info.file_path)

        object_dir = get_object_photos_dir(object)
        photo_path = object_dir + '0.jpeg'
        with open(photo_path, 'wb') as file:
            file.write(down_file)

        object.save_photos([photo_path])

    space = db.get_space_by_id(object.space)
    space_router_markup = get_space_router_markup(message.from_user.id, space)
    bot.send_message(message.from_user.id, f'Объект {object.name} успешно добавлен ✅', reply_markup=space_router_markup)
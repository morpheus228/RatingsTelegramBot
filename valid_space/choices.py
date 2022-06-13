from valid_space.views import *

user_data = {}


def start(message):
    space_id = db.get_user_current_space_id(message.from_user.id)
    objects_ids = db.get_object_features_from_space(space_id, 'id')

    if len(objects_ids) < 2:
        bot.send_message(message.from_user.id, 'Количество объектов меньше 2 штук. Добавте еще объектов, чтобы начать сравнения...')
    else:
        user_data[message.from_user.id] = {'space_id': space_id}
        send_objects_for_choice(message)


def send_objects_for_choice(message):
    space_id = user_data[message.from_user.id]['space_id']
    objects = db.get_objects_for_choice_from_space(space_id)

    user_data[message.from_user.id]['first_object_id'] = objects[0].id
    user_data[message.from_user.id]['second_object_id'] = objects[1].id
    user_data[message.from_user.id]['message_ids'] = []

    related_messages = []
    text_message, photo_messages = send_object(message, objects[0])
    related_messages.append(text_message)
    related_messages += photo_messages

    text_message, photo_messages = send_object(message, objects[1])
    related_messages.append(text_message)
    related_messages += photo_messages

    choice_keyboard = get_choice_keyboard(objects)
    db_bot.send_callback_message(message.from_user.id, text='Кто лучше???',
            reply_markup=choice_keyboard, space_id=space_id, related_messages=related_messages)


def send_object(message, object):
    text = f'''{object.name} \n{object.description}'''
    text_message = bot.send_message(message.from_user.id, text)

    photo_list = get_object_photos(object)

    if len(photo_list) != 0:
        photo_messages = bot.send_media_group(message.from_user.id, photo_list)
    else:
        photo_messages = [bot.send_message(message.from_user.id, 'Фотографий, к сожалению, нет...')]

    return text_message, photo_messages


def get_object_photos(object):
    photo_list = []
    for url in object.photos[:10]:
        photo = types.InputMediaPhoto(open(url, 'rb'))
        photo_list.append(photo)
    return photo_list


@bot.callback_query_handler(func=lambda call: call.verified and call.message.text == 'Кто лучше???')
def take_choice(call):
    db_bot.delete_callback_message(call.message)

    object1_id = user_data[call.from_user.id]['first_object_id']
    object2_id = user_data[call.from_user.id]['second_object_id']
    choice = int(call.data)
    space_id = db.get_object_by_id(object1_id).space

    if check_space_matching(call.from_user.id, space_id):
        db.add_choice(call.from_user.id, space_id, object1_id, object2_id, choice)
        send_objects_for_choice(call)


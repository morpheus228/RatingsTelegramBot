from valid_space.adding.views import *
from valid_space.adding.vk.parser import vk_group_parser
from valid_space.views import *
from checking import *

users_data = {}


@bot.callback_query_handler(func=lambda call: call.verified and
    (call.message.text == 'Выберите ИСТОЧНИК...') and (call.data == 'vk_group'))
def vk_group_adding(call):
    db_bot.edit_callback_message(text='Введите ID группы...', message=call.message, delete=True)
    bot.register_next_step_handler(call.message, take_group_id)


def take_group_id(message):
    group_id = message.text if not message.text.isnumeric() else int(message.text)
    group_id = vk_group_parser.check_existence(group_id)

    if not group_id:
        bot.send_message(message.from_user.id, '😥 Группы с таким ID не существует...')
    else:
        users_data[message.from_user.id] = {'group_id': group_id, 'filters': {},
                                            'space_id': db.get_user_current_space_id(message.from_user.id)}
        db_bot.send_callback_message(message.from_user.id, 'Нужны ли ФИЛЬТРЫ пользователей?',
                reply_markup=filters_availability_keyboard, space_id=db.get_user_current_space_id(message.from_user.id))


@bot.callback_query_handler(func=lambda call:  call.verified and
    call.message.text == 'Нужны ли ФИЛЬТРЫ пользователей?')
def take_filters_availability(call):
    if call.data == 'no':
        db_bot.edit_callback_message(text='Какие ФОТОГРАФИИ брать со страниц?',
                                     message=call.message, reply_markup=photo_selector_markup)
    elif call.data == 'yes':
        take_filters(call)


def take_filters(call):
    db_bot.edit_callback_message(text='Выберите пол:', message=call.message, reply_markup=sex_keyboard)


@bot.callback_query_handler(func=lambda call: call.verified and call.message.text == 'Выберите пол:')
def take_sex(call):
    if not call.data == 'any':
        users_data[call.from_user.id]['filters'] = {'sex': int(call.data)}

    db_bot.edit_callback_message(text='Какие ФОТОГРАФИИ брать со страниц?',
                                 message=call.message, reply_markup=photo_selector_markup)


@bot.callback_query_handler(func=lambda call: call.verified and
    call.message.text == 'Какие ФОТОГРАФИИ брать со страниц?')
def take_photo_selector(call):
    db_bot.delete_callback_message(call.message)
    users_data[call.from_user.id]['photo_selector'] = call.data
    add_objects(call)


def add_objects(call):
    user_id = call.from_user.id
    location_id = users_data[user_id]['group_id']
    space_id = users_data[user_id]['space_id']
    photo_selector = users_data[user_id]['photo_selector']
    filters = users_data[user_id]['filters']

    objects_generator = vk_group_parser.create_objects_generator(location_id, user_id, space_id, photo_selector, filters)
    users_data[user_id]['objects_generator'] = objects_generator
    users_data[user_id]['end'] = False

    send_object(call.from_user.id)


def send_object(user_id):
    try:
        status, object = next(users_data[user_id]['objects_generator'])
    except StopIteration:
        bot.send_message(user_id, f'Объекты кончились.')
        users_data[user_id]['end'] = True
    else:
        print(status)
        if status == 'Objects number limit exceeded':
            bot.send_message(user_id,
                             f'Превышен лимит по количеству объектов в одной комнает ({db.objects_number_limit} штук).')
            users_data[user_id]['end'] = True
        elif status in ['already added', 'deactivated', 'does not satisfy filters', 'error']:
            send_object(user_id)
        else:
            text, photo_list = object_view(object)
            if len(photo_list) > 0:
                photo_messages = bot.send_media_group(user_id, photo_list)
            else:
                photo_messages = [bot.send_message(user_id, 'Фотографий у объекта нет...')]

            db_bot.send_callback_message(user_id, text, parse_mode='Markdown', reply_markup=object_adding_keyboard,
                                         related_messages=photo_messages, space_id=users_data[user_id]['space_id'])
            users_data[user_id]['object_id'] = object.id


@bot.callback_query_handler(func=lambda call: call.verified and
        call.message.text.__contains__('Имя:') and call.data in ['skip', 'stop', 'add'])
def take_object_decision(call):
    user_data = users_data[call.from_user.id]
    db_bot.delete_callback_message(call.message)

    if call.data in ['skip', 'stop']:
        object_id = user_data['object_id']
        db.delete_object_from_space_by_id(object_id)

    if (not call.data == 'stop') and (not users_data[call.from_user.id]['end']):
        send_object(call.from_user.id)






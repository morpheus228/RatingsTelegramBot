from valid_space.adding.views import *
from valid_space.adding.vk.parser import vk_group_parser
from valid_space.views import *
from checking import *
from datetime import datetime

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
        db_bot.delete_callback_message(call.message)
        add_objects(call)
    elif call.data == 'yes':
        take_filters(call)


def take_filters(call):
    db_bot.edit_callback_message(text='Выберите пол:', message=call.message, reply_markup=sex_keyboard)


@bot.callback_query_handler(func=lambda call: call.verified and call.message.text == 'Выберите пол:')
def take_sex(call):
    if not call.data == 'any':
        users_data[call.from_user.id]['filters'] = {'sex': int(call.data)}

    db_bot.edit_callback_message(text='Выберите возраст:', message=call.message, reply_markup=age_keyboard)


def check_age(birthday, low_board=0, high_board=300):
    if birthday.count('.') == 2:
        birthday = datetime.strptime(birthday, "%d.%m.%Y")
        now = datetime.now()
        years = int((now - birthday).total_seconds() / 31536000)
        return low_board <= years <= high_board
    else:
        return True


@bot.callback_query_handler(func=lambda call: call.verified and call.message.text == 'Выберите возраст:')
def take_age(call):
    if call.data == 'up to 18':
        users_data[call.from_user.id]['filters']['bdate'] = lambda birthday: check_age(birthday, high_board=17)
    elif call.data == '18-30':
        users_data[call.from_user.id]['filters']['bdate'] = lambda birthday: check_age(birthday, low_board=18, high_board=30)
    elif call.data == '31-50':
        users_data[call.from_user.id]['filters']['bdate'] = lambda birthday: check_age(birthday, low_board=31, high_board=50)
    elif call.data == '50-70':
        users_data[call.from_user.id]['filters']['bdate'] = lambda birthday: check_age(birthday, low_board=51, high_board=70)
    elif call.data == 'more 70':
        users_data[call.from_user.id]['filters']['bdate'] = lambda birthday: check_age(birthday, low_board=71)

    db_bot.delete_callback_message(call.message)
    add_objects(call)


def add_objects(call):
    user_id = call.from_user.id
    location_id = users_data[user_id]['group_id']
    space_id = users_data[user_id]['space_id']
    filters = users_data[user_id]['filters']
    print(filters)
    objects_generator = vk_group_parser.create_objects_generator(location_id, user_id, space_id, filters)
    users_data[user_id]['objects_generator'] = objects_generator
    users_data[user_id]['end'] = False

    search_message = bot.send_message(user_id, f'🔎 Поиск объектов...')
    send_object(call.from_user.id, search_message)


def send_object(user_id, search_message):
    try:
        status, object = next(users_data[user_id]['objects_generator'])
    except StopIteration:
        bot.edit_message_text(chat_id=search_message.chat.id, message_id=search_message.id, text=f'Объекты кончились.')
        users_data[user_id]['end'] = True
    else:
        print(status)
        if status == 'Objects number limit exceeded':
            bot.edit_message_text(chat_id=search_message.chat.id, message_id=search_message.id,
                                  text=f'Превышен лимит по количеству объектов в одной комнает ({db.objects_number_limit} штук).')
            users_data[user_id]['end'] = True
        elif status in ['already added', 'deactivated', 'does not satisfy filters', 'error']:
            send_object(user_id, search_message)
        else:
            bot.delete_message(chat_id=search_message.chat.id, message_id=search_message.id)
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
        search_message = bot.send_message(call.from_user.id, f'🔎 Поиск объектов...')
        send_object(call.from_user.id, search_message)






from config import *
from telebot import types
from checking import check_creator_privilege

remove_markup = types.ReplyKeyboardRemove()


def get_space_router_markup(user_id, space):
    space_router_markup = types.ReplyKeyboardMarkup()
    space_router_markup_btn1 = types.KeyboardButton(text='Список объектов 👇')
    space_router_markup_btn2 = types.KeyboardButton(text='Добавить объекты 🔨')
    space_router_markup_btn3 = types.KeyboardButton(text='Начать сравнения ▶')
    space_router_markup_btn4 = types.KeyboardButton(text='Топ 🔝')
    space_router_markup_btn5 = types.KeyboardButton(text='Выйти из комнаты 🚶')

    if check_creator_privilege(user_id, space):
        space_router_markup.add(space_router_markup_btn1, space_router_markup_btn2)
    else:
        space_router_markup.add(space_router_markup_btn1)

    space_router_markup.add(space_router_markup_btn3, space_router_markup_btn4)
    space_router_markup.add(space_router_markup_btn5)

    return space_router_markup


def get_space_objects_keyboard(space_id):
    objects = db.get_objects_from_space(space_id)
    space_objects_keyboard = types.InlineKeyboardMarkup()

    for object in objects:
        space_objects_keyboard_btn = types.InlineKeyboardButton(text=object.name, callback_data=object.id)
        space_objects_keyboard.add(space_objects_keyboard_btn)

    return space_objects_keyboard


object_editor_keyboard = types.InlineKeyboardMarkup()
object_editor_keyboard_btn1 = types.InlineKeyboardButton(text='❌ Удалить', callback_data='delete')
object_editor_keyboard_btn2 = types.InlineKeyboardButton(text='🔙 Назад', callback_data='back')
object_editor_keyboard.add(object_editor_keyboard_btn1, object_editor_keyboard_btn2)


def get_choice_keyboard(objects):
    choice_keyboard = types.InlineKeyboardMarkup()
    object_editor_keyboard_btn1 = types.InlineKeyboardButton(text=objects[0].name, callback_data=objects[0].id)
    object_editor_keyboard_btn2 = types.InlineKeyboardButton(text=objects[1].name, callback_data=objects[1].id)
    choice_keyboard.add(object_editor_keyboard_btn1, object_editor_keyboard_btn2)
    return choice_keyboard


def object_view(object):
    text = f'*Имя:* {object.name}\n'
    text += f'*Описание:* {object.description}\n'

    photo_list = []
    for url in object.photos[:10]:
        photo = types.InputMediaPhoto(open(url, 'rb'))
        photo_list.append(photo)

    return text, photo_list


def get_top_view(top_list):
    top_view = types.InlineKeyboardMarkup()
    for i in range(len(top_list)):
        object = top_list[i]
        top_view.add(types.InlineKeyboardButton(text=f'{i+1}. {object.name}', callback_data=object.id))

    return top_view



from config import *
from telebot import types


def space_view(space_id):
    space = db.get_space_by_id(space_id)
    text = f'*Название:* {space.name}\n'
    text += f'*ID:* {space.id}\n'
    text += f"*Приватный:* {'да' if space.private else 'нет'}\n"
    text += f"*Пароль:* {'' if space.password is None else space.password}\n"
    text += f"*Кол-во объектов:* {db.get_objects_number_by_space_id(space_id)}"
    return text


def create_my_spaces_keyboard(creator_id):
    spaces = db.get_spaces_by_creator_id(creator_id)
    keyboard = types.InlineKeyboardMarkup()
    for space in spaces:
        space_button = types.InlineKeyboardButton(text=space.name, callback_data=space.id)
        keyboard.add(space_button)

    return keyboard


space_editor_keyboard = types.InlineKeyboardMarkup()
space_editor_keyboard_btn1 = types.InlineKeyboardButton(text='❌ Удалить', callback_data='delete')
space_editor_keyboard_btn2 = types.InlineKeyboardButton(text='🔙 Назад', callback_data='back')
space_editor_keyboard.add(space_editor_keyboard_btn1)
space_editor_keyboard.add(space_editor_keyboard_btn2)

space_type_markup = types.InlineKeyboardMarkup()
space_type_markup_btn1 = types.InlineKeyboardButton('🔐 Приватная', callback_data='private')
space_type_markup_btn2 = types.InlineKeyboardButton('🗽 Открытая', callback_data='public')
space_type_markup.add(space_type_markup_btn1, space_type_markup_btn2)

which_space_enter_markup = types.InlineKeyboardMarkup()
which_space_enter_markup_bnt1 = types.InlineKeyboardButton('В чужую', callback_data='not_my')
which_space_enter_markup_bnt2 = types.InlineKeyboardButton('В свою', callback_data='my')
which_space_enter_markup.add(which_space_enter_markup_bnt1, which_space_enter_markup_bnt2)

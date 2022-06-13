import telebot
from telebot import types
from config import db_bot, bot

# telebot.apihelper.ENABLE_MIDDLEWARE = True

objects_source_keyboard = types.InlineKeyboardMarkup()
objects_source_keyboard_btn1 = types.InlineKeyboardButton(text='Вручную', callback_data='manually')
objects_source_keyboard_btn2 = types.InlineKeyboardButton(text='Страница ВК', callback_data='vk_user')
objects_source_keyboard_btn3 = types.InlineKeyboardButton(text='Группа ВК', callback_data='vk_group')
objects_source_keyboard.add(objects_source_keyboard_btn1)
objects_source_keyboard.add(objects_source_keyboard_btn2, objects_source_keyboard_btn3)


@bot.message_handler(func=lambda m: m.text in ['/start', '/help', 'Главное меню 🔙'])
def menu(message):
    db_bot.send_callback_message(message.from_user.id, text='Выбирай, что сделать хочешь...',
                                 reply_markup=objects_source_keyboard, space_id=12423)


# @bot.middleware_handler(update_types=['callback_query'])
# def check_space_validity(bot_instance, call):
#     print(call.message.id)


if __name__ == '__main__':
    bot.infinity_polling()


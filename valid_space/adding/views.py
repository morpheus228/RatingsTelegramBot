from telebot import types

remove_markup = types.ReplyKeyboardRemove()


objects_source_keyboard = types.InlineKeyboardMarkup()
objects_source_keyboard_btn1 = types.InlineKeyboardButton(text='Вручную', callback_data='manually')
objects_source_keyboard_btn2 = types.InlineKeyboardButton(text='Страница ВК', callback_data='vk_user')
objects_source_keyboard_btn3 = types.InlineKeyboardButton(text='Группа ВК', callback_data='vk_group')
objects_source_keyboard.add(objects_source_keyboard_btn1)
objects_source_keyboard.add(objects_source_keyboard_btn2, objects_source_keyboard_btn3)

filters_availability_keyboard = types.InlineKeyboardMarkup()
filters_availability_keyboard_btn1 = types.InlineKeyboardButton(text='Да', callback_data='yes')
filters_availability_keyboard_btn2 = types.InlineKeyboardButton(text='Нет', callback_data='no')
filters_availability_keyboard.add(filters_availability_keyboard_btn1, filters_availability_keyboard_btn2)

sex_keyboard = types.InlineKeyboardMarkup()
sex_keyboard_btn1 = types.InlineKeyboardButton(text='Мужской', callback_data='2')
sex_keyboard_btn2 = types.InlineKeyboardButton(text='Женский', callback_data='1')
sex_keyboard_btn3 = types.InlineKeyboardButton(text='Любой', callback_data='any')
sex_keyboard.add(sex_keyboard_btn1, sex_keyboard_btn2)
sex_keyboard.add(sex_keyboard_btn3)

age_keyboard = types.InlineKeyboardMarkup()
age_keyboard_btn1 = types.InlineKeyboardButton(text='Младше 18 лет', callback_data='up to 18')
age_keyboard_btn2 = types.InlineKeyboardButton(text='18-30 лет', callback_data='18-30')
age_keyboard_btn3 = types.InlineKeyboardButton(text='31-50 лет', callback_data='31-50')
age_keyboard_btn4 = types.InlineKeyboardButton(text='50-70 лет', callback_data='50-70')
age_keyboard_btn5 = types.InlineKeyboardButton(text='Старше 70 лет', callback_data='more 70')
age_keyboard_btn6 = types.InlineKeyboardButton(text='Любой', callback_data='any')
age_keyboard.add(age_keyboard_btn6, age_keyboard_btn1)
age_keyboard.add(age_keyboard_btn2, age_keyboard_btn3)
age_keyboard.add(age_keyboard_btn4, age_keyboard_btn5)

no_description_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
no_description_markup_btn1 = types.KeyboardButton('🚫 Без описания')
no_description_markup.add(no_description_markup_btn1)

no_photo_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
no_photo_markup_btn1 = types.KeyboardButton('🚫 Без фотографии')
no_photo_markup.add(no_photo_markup_btn1)

photo_selector_markup = types.InlineKeyboardMarkup()
photo_selector_markup_btn1 = types.InlineKeyboardButton(text='Все', callback_data='all')
photo_selector_markup_btn2 = types.InlineKeyboardButton(text='С человеком', callback_data='with human')
photo_selector_markup_btn3 = types.InlineKeyboardButton(text='Без человека', callback_data='without human')
photo_selector_markup.add(photo_selector_markup_btn1)
photo_selector_markup.add(photo_selector_markup_btn2, photo_selector_markup_btn3)


object_adding_keyboard = types.InlineKeyboardMarkup()
object_adding_keyboard_btn1 = types.InlineKeyboardButton(text='Добавить', callback_data='add')
object_adding_keyboard_btn2 = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
object_adding_keyboard_btn3 = types.InlineKeyboardButton(text='Остановить добавления', callback_data='stop')
object_adding_keyboard.add(object_adding_keyboard_btn1, object_adding_keyboard_btn2)
object_adding_keyboard.add(object_adding_keyboard_btn3)
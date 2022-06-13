from telebot import types

remove_markup = types.ReplyKeyboardRemove()

router_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
router_markup_btn1 = types.KeyboardButton("Зайти в комнату 🔘")
router_markup_btn2 = types.KeyboardButton("Создать комнату 🔨")
router_markup_btn3 = types.KeyboardButton("Мои комнаты 👇")
router_markup.add(router_markup_btn3, router_markup_btn2)
router_markup.add(router_markup_btn1)

choose_deleting_way_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
choose_deleting_way_markup_btn1 = types.KeyboardButton('По имени и фамилии')
choose_deleting_way_markup_btn2 = types.KeyboardButton('Лента')
choose_deleting_way_markup.add(choose_deleting_way_markup_btn1)
choose_deleting_way_markup.add(choose_deleting_way_markup_btn2)

deleting_tape_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
deleting_tape_markup_btn1 = types.KeyboardButton('Удалить')
deleting_tape_markup_btn2 = types.KeyboardButton('Оставить')
deleting_tape_markup_btn3 = types.KeyboardButton('Выйти')
deleting_tape_markup.add(deleting_tape_markup_btn1)
deleting_tape_markup.add(deleting_tape_markup_btn2)
deleting_tape_markup.add(deleting_tape_markup_btn3)


def create_objects_choice_markup(objects):
    objects_choice_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    objects_choice_markup_btn1 = types.KeyboardButton(f"1. {objects[0].name}")
    objects_choice_markup_btn2 = types.KeyboardButton(f"2. {objects[1].name}")
    objects_choice_markup_btn3 = types.KeyboardButton("Выйти")
    objects_choice_markup.add(objects_choice_markup_btn1)
    objects_choice_markup.add(objects_choice_markup_btn2)
    objects_choice_markup.add(objects_choice_markup_btn3)
    return objects_choice_markup












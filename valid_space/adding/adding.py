from valid_space.adding.views import *
from config import *
from checking import check_creator_privilege
from valid_space.adding.vk import user_adding, group_adding
from valid_space.adding import manually_adding


def start(message):
    space_id = db.get_user_current_space_id(message.from_user.id)
    if check_creator_privilege(message.from_user.id, db.get_space_by_id(space_id)):
        status = db.check_objects_number_limit(space_id)

        if status:
            db_bot.send_callback_message(message.from_user.id, 'Выберите ИСТОЧНИК...',
                                         reply_markup=objects_source_keyboard, space_id=space_id)
        else:
            bot.send_message(message.from_user.id,
                             f'Превышен лимит по количеству объектов в одной комнает ({db.objects_number_limit} штук).')
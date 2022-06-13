from config import *


@bot.middleware_handler(update_types=['callback_query'])
def check_space_validity(bot_instance, call):
    call.verified = True
    space_id = db_bot.get_space_by_callback(call.message)
    cur_space_id = db.get_user_current_space_id(call.from_user.id)

    if space_id is not None:
        if not (space_id[0] == cur_space_id):
            call.verified = False
            db_bot.delete_callback_message(call.message)


@bot.middleware_handler(update_types=['message'])
def check_new_user(bot_instance, message):
    users = db.get_user_ids()
    if message.from_user.id not in users:
        db.add_registered_user(message)


def check_creator_privilege(user_id, space):
    return user_id == space.creator

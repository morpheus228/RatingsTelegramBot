from config import *
from valid_space.views import get_top_view


def start(user_id):
    space_id = db.get_user_current_space_id(user_id)
    space = db.get_space_by_id(space_id)
    top_list = db.get_objects_top_from_space(space_id)
    top_list = top_list[:10]
    top_view = get_top_view(top_list)
    db_bot.send_callback_message(user_id, text=f'Топ 10 объектов комнаты {space.name}:',
                                 reply_markup=top_view, space_id=space_id)


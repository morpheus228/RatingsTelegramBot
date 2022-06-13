from config import *
import main


def start(message):
    space_id = db.get_user_current_space_id(message.from_user.id)
    space = db.get_space_by_id(space_id)

    bot.send_message(message.from_user.id, f'Ты вышел из комнаты "{space.name}"')
    main.menu(message)

    db.alter_user_current_space(message.from_user.id, 'null')
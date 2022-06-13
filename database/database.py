import psycopg2
import pandas as pd
import random
import warnings
import os
import shutil
import json

warnings.filterwarnings('ignore')


class Database:
    with open('database/config.json', 'r') as config_file:
        config_information = json.load(config_file)

    connection = psycopg2.connect(**config_information)
    cursor = connection.cursor()

    def __init__(self, spaces_number_limit=10, objects_number_limit=50):
        self.spaces_number_limit = spaces_number_limit
        self.objects_number_limit = objects_number_limit

    class Space:
        def __init__(self, creator=None, name=None, password=None, id=None):
            self.id = id
            self.connection = Database.connection
            self.cursor = Database.cursor
            self.creator = creator
            self.name = name
            self.password = password

            if password is not None:
                self.private = True
            else:
                self.private = False

        def save(self):
            if self.private:
                self.cursor.execute(f'''INSERT INTO spaces(creator, name, private, password)
                    VALUES ({self.creator}, '{self.name}', true, '{self.password}') RETURNING id;''')
            else:
                self.cursor.execute(f'''INSERT INTO spaces(creator, name, private)
                    VALUES ({self.creator}, '{self.name}', false) RETURNING id;''')

            self.id = self.cursor.fetchone()[0]
            self.connection.commit()
            os.mkdir(f'photos/{self.id}')

        def from_entry(self, entry):
            self.id = entry[0]
            self.name = entry[1]
            self.creator = entry[2]
            self.private = entry[3]
            self.password = entry[4]
            return self

    class Object:
        def __init__(self, creator=None, space=None, source=None,
                     name=None, description=None, photos=None, id=None, source_id=0):
            self.id = id
            self.connection = Database.connection
            self.cursor = Database.cursor

            self.creator = creator
            self.space = space
            self.source = source
            self.source_id = source_id
            self.name = name
            self.description = description
            self.photos = photos

        def save(self):
            self.cursor.execute(f'''INSERT INTO objects(creator, space, source, source_id, name, description)
            VALUES ({self.creator}, {self.space}, '{self.source}', {self.source_id}, '{self.name}', '{self.description}')
            RETURNING id;''')
            self.id = self.cursor.fetchone()[0]
            os.mkdir(f'photos/{self.space}/{self.id}')
            return self.id

        def save_photos(self, photos):
            self.photos += photos
            for photo in self.photos:
                self.cursor.execute(f'''INSERT INTO photos(object, url) VALUES ({self.id}, '{photo}');''')

            self.connection.commit()

        def from_entry(self, entry):
            photos = Database.get_photos_by_object_id(self, entry[0])
            self.id = entry[0]
            self.name = entry[1]
            self.description = entry[2]
            self.source = entry[3]
            self.source_id = entry[4]
            self.creator = entry[5]
            self.space = entry[6]
            self.photos = photos
            return self

    def get_photos_by_object_id(self, object_id):
        self.cursor.execute(f'SELECT * FROM photos WHERE object = {object_id}')
        photos = [photo[2] for photo in self.cursor.fetchall()]
        return photos

    def get_object_by_id(self, object_id):
        self.cursor.execute(f'SELECT * FROM objects WHERE id={object_id};')
        entry = self.cursor.fetchone()
        object = self.Object().from_entry(entry)
        return object

    def get_object_features_from_space(self, space_id, feature):
        self.cursor.execute(f'SELECT {feature} FROM objects WHERE space={space_id};')
        features = [i[0] for i in self.cursor.fetchall()]
        return features

    def get_objects_from_space(self, space_id):
        ids = self.get_object_features_from_space(space_id, 'id')
        objects = [self.get_object_by_id(id) for id in ids]
        return objects

    def get_objects_for_choice_from_space(self, space_id):
        objects = self.get_objects_from_space(space_id)
        if len(objects) < 2:
            return False
        else:
            chosen_objects = random.choices(objects, k=2)
            while chosen_objects[0] == chosen_objects[1]:
                chosen_objects = random.choices(objects, k=2)
            return chosen_objects

    # Get source ids those objects, which have been already added from some source
    def get_source_object_ids_from_space(self, space_id, source):
        self.cursor.execute(f'''SELECT source_id FROM objects
                            WHERE space={space_id} AND source='{source}';''')
        source_ids = [i[0] for i in self.cursor.fetchall()]
        return source_ids

    def get_objects_top_from_space(self, space_id):
        df1 = pd.read_sql(f'''SELECT objects.id, COUNT(*)
                    FROM choices
                    JOIN objects ON choices.choice = objects.id
                    WHERE objects.space={space_id}
                    GROUP BY objects.id''', self.connection)

        df2 = pd.read_sql(f'''SELECT objects.id, COUNT(*)
                    FROM choices
                    JOIN objects ON (choices.object1 = objects.id OR choices.object2 = objects.id)
                    WHERE objects.space={space_id}
                    GROUP BY objects.id;''', self.connection)

        df1.index = df1.id
        df2.index = df2.id

        top_list = []
        for object in df2.iterrows():
            object_id = object[0]
            if object_id in list(df1.index):
                value = df1.loc[object_id, 'count'] / df2.loc[object_id, 'count']
            else:
                value = 0
            top_list.append([self.get_object_by_id(object_id), value])

        sorted_top_list = sorted(top_list, key=lambda x: x[1], reverse=True)
        sorted_top_list = [i[0] for i in sorted_top_list]
        return sorted_top_list

    def get_all_space_features(self, feature):
        self.cursor.execute(f'SELECT {feature} FROM spaces;')
        features = [i[0] for i in self.cursor.fetchall()]
        return features

    def get_space_by_id(self, space_id):
        self.cursor.execute(f'SELECT * FROM spaces WHERE id={space_id};')
        entry = self.cursor.fetchone()
        space = self.Space().from_entry(entry)
        return space

    def get_space_features_by_creator_id(self, creator_id, feature):
        self.cursor.execute(f'SELECT {feature} FROM spaces WHERE creator = {creator_id}')
        features = [i[0] for i in self.cursor.fetchall()]
        return features

    def get_spaces_by_creator_id(self, creator_id):
        ids = self.get_space_features_by_creator_id(creator_id, 'id')
        spaces = [self.get_space_by_id(id) for id in ids]
        return spaces

    def get_objects_number_by_space_id(self, space_id):
        self.cursor.execute(f'''SELECT COUNT(*) FROM objects WHERE space={space_id};''')
        return self.cursor.fetchone()[0]

    def get_spaces_number_by_user_id(self, user_id):
        self.cursor.execute(f'''SELECT COUNT(*) FROM spaces WHERE creator={user_id};''')
        return self.cursor.fetchone()[0]

    def alter_user_current_space(self, user_id, space_id):
        self.cursor.execute(f'UPDATE users SET current_space={space_id} WHERE id = {user_id}')
        self.connection.commit()

    def get_user_current_space_id(self, user_id):
        self.cursor.execute(f'SELECT current_space FROM users WHERE id = {user_id}')
        current_space = self.cursor.fetchone()[0]
        return current_space

    def get_user_ids(self):
        self.cursor.execute(f'SELECT id FROM users')
        ids = [i[0] for i in self.cursor.fetchall()]
        self.connection.commit()
        return ids

    def delete_object_from_space_by_id(self, object_id):
        object = self.get_object_by_id(object_id)
        object_dir = f'photos/{str(object.space)}/{str(object.id)}'
        shutil.rmtree(object_dir)

        self.cursor.execute(f'''DELETE FROM objects WHERE id='{object_id}';''')
        self.connection.commit()

    def delete_space_by_id(self, space_id):
        space_dir = f'photos/{str(space_id)}'
        shutil.rmtree(space_dir)

        self.cursor.execute(f'''DELETE FROM spaces WHERE id='{space_id}';''')
        self.connection.commit()

    def add_registered_user(self, message):
        self.cursor.execute(f'''INSERT INTO users VALUES (
                         {message.from_user.id}, {message.from_user.is_bot}, '{message.from_user.first_name}',
                        '{message.from_user.username}', '{message.from_user.last_name}', '{message.from_user.language_code}', {'null'});''')
        self.connection.commit()

    def add_choice(self, user_id, space_id, object_id_1, object_id_2, choice):
        self.cursor.execute(f'''INSERT INTO choices(executor, space, object1, object2, choice)
                       VALUES ({user_id}, {space_id}, {object_id_1}, {object_id_2}, {choice});''')
        self.connection.commit()

    def check_objects_number_limit(self, space_id):
        if self.get_objects_number_by_space_id(space_id) > self.objects_number_limit:
            return False
        else:
            return True

    def check_spaces_number_limit(self, user_id):
        if self.get_spaces_number_by_user_id(user_id) >= self.spaces_number_limit:
            return False
        else:
            return True

    class DBBot:
        def __init__(self, bot):
            self.bot = bot
            self.connection = Database.connection
            self.cursor = Database.cursor

        def send_callback_message(self, user_id, text, reply_markup, space_id, related_messages=None, **kwargs):
            message = self.bot.send_message(user_id, text, reply_markup=reply_markup, **kwargs)
            related_messages = [] if related_messages is None else related_messages

            self.cursor.execute(f'''INSERT INTO messages(id, sender) VALUES
                                ({message.id}, {user_id})''')

            self.cursor.execute(f'''INSERT INTO space_callbacks(message, space) VALUES
                                ({message.id}, {space_id})''')

            for related_message in related_messages:
                self.cursor.execute(f'''INSERT INTO messages(id, sender, main_message) VALUES
                                ({related_message.id}, {user_id}, {message.id})''')

            self.connection.commit()
            return message

        def delete_callback_message(self, message):
            self.bot.delete_message(chat_id=message.chat.id, message_id=message.id)

            self.cursor.execute(f'''SELECT id FROM messages WHERE main_message={message.id}''')
            for related_message in self.cursor.fetchall():
                self.bot.delete_message(chat_id=message.chat.id, message_id=related_message[0])

            self.cursor.execute(f'''DELETE FROM messages WHERE id={message.id}''')
            self.connection.commit()

        def get_space_by_callback(self, message):
            self.cursor.execute(f'''SELECT space FROM space_callbacks WHERE message={message.id}''')
            return self.cursor.fetchone()

        def edit_callback_message(self, text, message, delete=False, **kwargs):
            self.bot.edit_message_text(text=text, chat_id=message.chat.id, message_id=message.id, **kwargs)
            if delete:
                self.cursor.execute(f'''DELETE FROM messages WHERE id={message.id}''')


import json
import time
from abc import abstractmethod, ABC

from urllib.request import urlopen as urlopen
from urllib.parse import urlencode as urlencode

from valid_space.adding.photo_iteractions import *
from photo_selector.selector import PhotoSelector
from config import *


class VkParser(ABC):
    def __init__(self, token_path='valid_space/adding/vk/token.txt',
                 photos_num=20, max_photos_num_for_selection=32, threshold_value=0.3):
        with open(token_path, 'r') as file:
            self.token = file.read().strip()
            self.photos_num = photos_num
            self.max_photos_num_for_selection = max_photos_num_for_selection

            self.selector = PhotoSelector()
            self.threshold_value = threshold_value

    @abstractmethod
    def check_existence(self, some_id):
        pass

    def make_request(self, method, **kwargs):
        kwargs['access_token'] = self.token
        kwargs['v'] = '5.131'

        params = urlencode(kwargs)
        request_str = f'https://api.vk.com/method/{method}?{params}'

        response = urlopen(request_str).read()
        response = bytes.decode(response)
        response = json.loads(response)

        if 'error' in response.keys():
            return 'error'
        else:
            return response['response']

    def add_object(self, vk_object_id, user_id, space_id, description, photo_selector, filters={}):
        fields = 'photo_400_orig' + ', ' + ', '.join(list(filters.keys()))
        get_object_response = self.make_request('users.get', user_ids=vk_object_id, fields=fields)[0]
        name = f"{get_object_response['first_name']} {get_object_response['last_name']}"
        object = db.Object(source='vk', source_id=vk_object_id, name=name, creator=user_id,
                           space=space_id, description=description, photos=[])

        already_added_objects = db.get_source_object_ids_from_space(space_id, 'vk')
        if vk_object_id in already_added_objects:
            status = 'already added'

        elif 'deactivated' in get_object_response.keys():
            status = 'deactivated'

        else:
            for filter_key in filters.keys():
                if not get_object_response[filter_key] == filters[filter_key]:
                    status = 'does not satisfy filters'
                    break
            else:
                try:
                    object.save()
                    photo_paths = self.add_object_photos(get_object_response, object, status=photo_selector)
                    object.save_photos(photo_paths)
                    status = 'successfully'

                except BaseException as error:
                    status = 'error'

        return status, object

    def add_object_photos(self, get_object_response, object, status):
        object_dir = get_object_photos_dir(object)

        if not get_object_response['can_access_closed']:
            photo_urls = [get_object_response['photo_400_orig']]
        else:
            get_object_photos_response = self.make_request('photos.getAll', owner_id=object.source_id)
            photo_urls = [item['sizes'][-1]['url'] for item in get_object_photos_response['items']]
            photo_urls = photo_urls[:self.max_photos_num_for_selection]

        if status == 'all':
            dir_list = self.download_photos_without_selection(photo_urls, object_dir)
        elif status == 'with human':
            dir_list = self.download_photos_with_selection(photo_urls, object_dir)
        elif status == 'without human':
            dir_list = self.download_photos_with_selection(photo_urls, object_dir, reverse=True)

        return dir_list

    def download_photos_with_selection(self, photo_urls, object_dir, reverse=False):
        dir_list = []
        photos_list = []

        for photo_url in photo_urls:
            photo = download_photo(photo_url)
            if photo:
                photos_list.append(photo)

        if len(photos_list) > 0:
            predictions = self.selector.select(photos_list)

            for pk in range(len(photos_list)):
                if (predictions[pk][0] >= self.threshold_value) ^ reverse:
                    photo_dir = f"{object_dir}/{pk}.jpeg"
                    photos_list[pk].save(photo_dir)
                    dir_list.append(photo_dir)

                    if len(dir_list) == self.photos_num:
                        break

        return dir_list

    def download_photos_without_selection(self, photo_urls, object_dir):
        dir_list = []
        photos_list = []

        for photo_url in photo_urls:
            photo = download_photo(photo_url)
            if photo:
                photos_list.append(photo)

        for pk in range(len(photos_list)):
            photo_dir = f"{object_dir}/{pk}.jpeg"
            photos_list[pk].save(photo_dir)
            dir_list.append(photo_dir)

            if len(dir_list) == self.photos_num:
                break

        return dir_list


class VkUserParser(VkParser):
    def __init__(self):
        super().__init__()

    def check_existence(self, user_id):
        get_chat_response = self.make_request('users.get', user_ids=user_id)
        if len(get_chat_response) == 0:
            return False
        else:
            return get_chat_response[0]['id']


class VkCollectionParser(VkParser):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_members(self, location_id):
        pass

    def create_objects_generator(self, location_id, user_id, space_id, photo_selector, filters={}):
        description, objects = self.get_members(location_id)

        for vk_object_id in objects:
            status = db.check_objects_number_limit(space_id)
            if not status:
                yield 'Objects number limit exceeded'
                break
            else:
                time.sleep(0.5)
                yield self.add_object(vk_object_id, user_id, space_id, description, photo_selector, filters)


class VkGroupParser(VkCollectionParser):
    def __init__(self):
        super().__init__()

    def check_existence(self, group_id):
        get_group_response = self.make_request('groups.getById', group_id=group_id)
        if get_group_response == 'error':
            return False
        else:
            return get_group_response[0]['id']

    def get_members(self, group_id):
        get_group_response = self.make_request('groups.getById', group_id=group_id)[0]
        description = get_group_response['name']

        get_group_members_response = self.make_request('groups.getMembers', group_id=group_id)
        objects = get_group_members_response['items']

        return description, objects


class VkChatParser(VkCollectionParser):
    def __init__(self):
        super().__init__()

    def check_existence(self, chat_id):
        get_chat_response = self.make_request('messages.getChat', chat_id=chat_id)
        if get_chat_response == 'error':
            return False
        else:
            return get_chat_response[0]['id']

    def get_members(self, chat_id):
        get_chat_response = self.make_request('messages.getChat', chat_id=chat_id)
        description = get_chat_response['title']
        objects = get_chat_response['users']

        return description, objects

vk_user_parser = VkUserParser()
vk_chat_parser = VkChatParser()
vk_group_parser = VkGroupParser()
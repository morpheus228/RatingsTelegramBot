import requests
import os
from PIL import Image


def get_object_photos_dir(object):
    photos_dir = 'photos/'
    space_dir = f'{str(object.space)}'
    object_dir = f'{str(object.id)}'
    directory = photos_dir + space_dir + '/' + object_dir + '/'
    return directory


def download_photo(url):
    try:
        photo_response = requests.get(url, stream=True).raw
        photo = Image.open(photo_response)
        return photo
    except:
        return False

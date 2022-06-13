from urllib.request import urlopen as urlopen
from urllib.parse import urlencode as urlencode
import json
import argparse

parser = argparse.ArgumentParser(description='Taking VK token')
parser.add_argument('login')
parser.add_argument('password')


def auth(login, pwd):
    params = {}
    params['grant_type'] = 'password'
    params['client_id'] = '2274003'
    params['client_secret'] = 'hHbZxrka2uZ6jB1inYsH'
    params['username'] = login
    params['password'] = pwd
    request_str = 'https://oauth.vk.com/token?%s' % urlencode(params)
    r = urlopen(request_str).read()
    response = bytes.decode(r)
    json_data = json.loads(response)
    if 'error' in json_data:
        return {'error': 'Wrong auth data'}
    if not 'error' in json_data and not 'access_token' in json_data:
        return {'error': 'Unknown error'}

    with open('token.txt', 'w') as file:
        file.write(json_data['access_token'])


if __name__ == '__main__':
    args = parser.parse_args()
    auth(args.login, args.password)
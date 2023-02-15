import requests
import json
import datetime
from tqdm import tqdm
import configparser
from time import sleep


config = configparser.ConfigParser()
config.read("settings.ini")
access_token = config.get('token', 'access_token')
user_name = config.get('token', 'user_name')
token_ya = config.get('token', 'token_ya')
# print(access_token, user_name, token_ya)


def time_convert(time_unix):
    time_bc = datetime.datetime.fromtimestamp(time_unix)
    str_time = time_bc.strftime('%Y-%m-%d time %H-%M-%S')
    return str_time


class VK:

    def __init__(self, access_token, user_name, version='5.131'):
        self.token = access_token
        self.id = user_name
        self.version = version
        self.params = {
            'access_token': self.token,
            'owner_id': self.id,
            'v': self.version}

 
      
    # def get_users_name(self, user_name):
    #     url = 'https://api.vk.com/method/utils.resolveScreenName'
    #     params = {
    #         'access_token': access_token,
    #         'screen_name': user_name,
    #         'v': '5.131'
    #     }
    #     response = requests.get(url, params=params)
    #     if 'user_name'.isdigit():
    #         return user_name
    #     else:
    #         n_n = response.json()['response']['odject_id']
    #         return n_n


    def users_info(self, user_name):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params}).json()
        user_name =  response['response']['id']
        return user_name


    def json_file(self, user_name, album_id, f_count):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': user_name,
                  'album_id': album_id,
                  'count': f_count,
                  'rev': 0,
                  'extended': 1,
                  'photo_sizes': 1
                  }
        response = requests.get(url, params={**self.params, **params})
        data = response.json()['response']['items']
        return data


    def photos_size(self):
        max_size = {}
        data = vk.json_file(user_name, album_id, f_count)
        for ph in data:
            file_name = f'{ph["likes"]["count"]}.jpg'
            time_warp = time_convert(ph['date'])
            file_names = f'{ph["likes"]["count"]}{time_warp}.jpg'
            size_dict = {'s': 0, 'm': 1, 'o': 2, 'p': 3,
                         'q': 4, 'r': 5, 'x': 6, 'y': 7, 'z': 8, 'w': 9}
            max_size_ph = max(ph['sizes'], key=lambda x: size_dict[x['type']])
            if file_name not in max_size.keys():
                max_size[file_name] = {max_size_ph['type']: max_size_ph['url']}
            else:
                max_size[file_names] = {max_size_ph['type']: max_size_ph['url']}
        return max_size


class Yandex:

    def __init__(self, token_ya):
        self.ya_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.token = token_ya
        self.headers = {
            'Authorization': f'OAuth {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }


    def ya_path_folder(self, folder_name):
        self.ya_url = "https://cloud-api.yandex.net/v1/disk/resources"
        upload_photo(self)
        if requests.get(f'{self.ya_url}?path={folder_name}', headers=self.headers).status_code != 200:
            requests.put(f'{self.ya_url}?path={folder_name}',
                         headers=self.headers)
            print(f'\nПапка {folder_name} успешно создана!\n')
        else:
            print(f'\nПапка {folder_name} уже существует\n')
        return folder_name


def upload_photo(self):
    file_json = []
    _photo = vk.photos_size()
    for k, dict_v in tqdm(_photo.items(), desc='Идет копирование фотографий: ', colour='#00ff00'):
        sleep(0.1)       
        self.path_file = f'/{folder_name}/{k}.jpg'
        self.params = {'path': self.path_file, 'url': dict_v.values()}
        for key in dict_v.keys():
            json_photo = {"file_name": f'{k}.jpg', "size": f'{key}'}
            file_json.append(json_photo) 
    return  file_json


# user_name = input('Введите id пользователя VK или Screen_Name ): ')

vk = VK(access_token, user_name)
ya = Yandex(token_ya)
user_name = vk.users_info(user_name)


while True:
    album = input(
        """Какие фотографии Вас интересуют? \n"1" Фотографии со стены или "2" Фотографии профиля:  """)
    if album < '1' or album > '2':
        print('Попробуйте снова, выберите "1" или "2"')
        break
    elif album == '1':
        album_id = 'wall'
    elif album == '2':
        album_id = 'profile'
    f_count = int(input('Введите количество фото для скачивания: '))
    if f_count == 0 or f_count > 100:
        f_count = 5
        print('Установленно значение по умолчанию - 5 фото.')
    folder_name = input('Введите название папки для сохранения фото: ')
    file_up = []
    # token_ya = input("""Введите токен от Я-Диска: """)
    if requests.get(f'{ya.ya_url}?path={folder_name}', headers=ya.headers).status_code == 403:
        print('Введены неверные данные, проверьте Ваш токен!')
        break
    else:
        j_file = upload_photo(folder_name)
  
    file_name = 'VK_photo.json'
    with open(file_name, 'w') as f:
        json.dump(file_up, f, indent=2)
    with open(folder_name, 'w') as t:
        t.write(file_name)
    print('Загрузка фото прошла успешно!')
    break

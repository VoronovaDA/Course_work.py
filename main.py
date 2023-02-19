import requests
import json
import datetime
from tqdm import tqdm
import configparser
from time import sleep




config = configparser.ConfigParser()
config.read("settings.ini")
access_token = config["token"]["access_token"]
user_name = config["token"]["user_name"]
token_ya = config["token"]["token_ya"]
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

        
    def users_info(self, user_name):
        url = 'https://api.vk.com/method/users.get'
        params = {"user_ids": f"{self.id}"}
        user_name = requests.get(url, params={**self.params, **params})
        # user_name=([i[k] for i in  response['response'] for k in i])
        return user_name.json()['response'][0]['id']
             

    def photo_vk(self, user_name):
        url = 'https://api.vk.com/method/photos.get'
        params = ({'owner_id': user_name,
                  'album_id': album_id,
                  'count': f_count,
                  'rev': 0,
                  'extended': 1,
                  'photo_sizes': 1
                  })
        res = requests.get(url=url, params={**self.params, **params}).json()
        data = res['response']['items']
        return data


    def json_file(self):
        max_size = {}
        data_f = vk.photo_vk(user_name)
        for ph in data_f:
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
            'Accept': 'application/json'}


    def ya_path_folder(self, folder_name):
        self.ya_url = "https://cloud-api.yandex.net/v1/disk/resources"
        if requests.get(f'{self.ya_url}?path={folder_name}', headers=self.headers).status_code != 200:
            requests.put(f'{self.ya_url}?path={folder_name}',
                         headers=self.headers)
            print(f'\nПапка {folder_name} успешно создана!\n')
        else:
            print(f'\nПапка {folder_name} уже существует!\n')
        return folder_name


    def upload_photo(self):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        ya.ya_path_folder(folder_name)
        file_json = []
        _photo = vk.json_file()
        for k, dict_v in tqdm(_photo.items(), desc='Идет копирование фотографий: ', colour='#00ff00'):
            sleep(0.1) 
            path_file = f'{folder_name}/{k}.jpg'              
            self.params = {'path': path_file, 'url': dict_v.values()}
            res = requests.post(upload_url, params=self.params, headers=self.headers)
            status = res.status_code
            for key in dict_v.keys():
                json_photo = {"file_name": f'{folder_name}/{k}.jpg', "size": f'{key}'}
                file_json.append(json_photo) 
            if status < 400:
                print(f'Фотографии загружены на Я-Диск!')
            else:
                print('Ошибка загрузки! Введены неверные данные, проверьте Ваш токен!')
                break
        return file_json


#user_name = input("Здравствуйте! \nВведите id или screen_name пользователя VK: ")
vk = VK(access_token, user_name)
ya = Yandex(token_ya)
user_name = vk.users_info(user_name)


while True:
    #token_ya = input("""Введите токен от Я-Диска: """)
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
    upload_file = ya.upload_photo()   
    with open('my_VK_photo.json', 'w') as f:
        json.dump(upload_file, f, indent=2)
    with open(folder_name, 'w') as t:
        t.write('my_VK_photo.json')
    
    break

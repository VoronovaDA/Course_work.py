import requests
import json
import datetime
from tqdm import tqdm
from TOKEN_YA import token_ya
from TOKEN_VK import access_token, users_id
from time import sleep


def time_convert(time_unix):
        time_bc = datetime.datetime.fromtimestamp(time_unix)
        str_time = time_bc.strftime('%Y-%m-%d time %H-%M-%S')
        return str_time

class VK:
    def __init__(self, access_token, users_id, version='5.131'):
        self.token = access_token
        self.id = users_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def json_file(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id,
                  'album_id': album_id,
                  'count': 5,
                  'rev': 0,
                  'extended': 1,
                  'photo_sizes': 1
                  }
        response = requests.get(url, params={**self.params, **params})
        data = response.json()
        return data

    def photos_size(self):
        max_size = {}
        data = self.json_file()
        photo = data['response']['items']
        for ph in photo:
            file_name = f'{ph["likes"]["count"]}.jpg'
            time_warp = time_convert(ph['date'])
            file_names = f'{ph["likes"]["count"]}{time_warp}.jpg'
            size_dict = {'s': 0, 'm': 1, 'o': 2, 'p': 3, 'q': 4, 'r': 5, 'x': 6, 'y': 7, 'z': 8, 'w': 9}
            max_size_ph = max(ph['sizes'], key=lambda x: size_dict[x['type']])
            if file_name not in max_size.keys():
                max_size[file_name] = {max_size_ph['type']: max_size_ph['url']}
            else:
                max_size[file_names] = {max_size_ph['type']: max_size_ph['url']}
        return max_size


class Yandex:
    def __init__(self,token_ya: str):
        self.token = token_ya
        
    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}', 'Accept': 'application/json'}

    def create_folder(self, folder_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        if requests.get(f'{url}?path={folder_name}', headers=self.get_headers()).status_code != 200:
            requests.put(f'{url}?path={folder_name}', headers=self.get_headers())
            print(f'\nПапка {folder_name} успешно создана в корневом каталоге Яндекс диска\n')
        else:
            print(f'\nПапка {folder_name} уже существует\n')
        return folder_name

    def upload_photo(self):
        file_json = []
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload/'
        self.vk_ = VK(access_token, users_id)
        _photo = self.vk_.photos_size()
        self.create_folder(folder_name)
        for k, dict_v in tqdm(_photo.items(), desc='Идет копирование фотографий: ', colour='#00ff00'):
            sleep(0.1)       
            path_file = f'/{folder_name}/{k}.jpg'
            response = requests.post(url, headers=self.get_headers(), params={'path': path_file, 'url': dict_v.values()}).json()
            for key in dict_v.keys():
                json_photo = {"file_name": f'{k}.jpg', "size": f'{key}'}
                file_json.append(json_photo) 
        return  file_json


if __name__ == '__main__':

    # users_id = input('Введите id пользователя VK: ')
    # token_ya = input ('Введите token от Яндекс-Диска: ')

    
    album = input("""Какие фотографии Вас интересуют? \n"1" - фотографии со стены или "2" - фотографии профиля:  """)
    if album == '1':
        album_id = 'wall'
    elif album == '2':
        album_id = 'profile'
    else:
        print('Попробуйте снова, выберите "1" или "2"')
           

    ya = Yandex(token_ya)
    vk = VK(access_token, users_id)
        
    folder_name = 'VK_photo_copies.txt'
    name_f = 'my_VK_photo.json'
        
    j_file = ya.upload_photo()
    
    with open(name_f, 'w') as f:            
        json.dump(j_file, f, indent=2)
    with open(folder_name, 'w') as t:                
        t.write(name_f)
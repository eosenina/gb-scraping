# Задание 2
# Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

# Выборка видео "в тренде" из youtube:
import os

import requests
import json

key = os.environ.get('YOUTUBE_KEY')
url = f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&chart=mostPopular'
headers = {'Accept': 'application/json'}
params = {'key': key,
          'regionCode': 'RU'}

response = requests.get(url, headers=headers, params=params)
data = response.json()
for vd in data['items']:
    print(vd['snippet'])

with open('youtube.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
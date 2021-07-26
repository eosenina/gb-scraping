# Задание 1
# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев
# для конкретного пользователя, сохранить JSON-вывод в файле *.json.

# curl \
#   -H "Accept: application/vnd.github.v3+json" \
#   https://api.github.com/users/USERNAME/repos
import requests
import json

user_name = 'eosenina'
url = f'https://api.github.com/users/{user_name}/repos'
headers = {'Accept': 'application/vnd.github.v3+json'}

response = requests.get(url, headers=headers)
data = response.json()
for repo in data:
    print(repo['name'])

with open('repo_list.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

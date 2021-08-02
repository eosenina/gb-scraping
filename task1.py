# Задание 1
# Необходимо собрать информацию о вакансиях на вводимую должность
# (используем input или через аргументы получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию).
# Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
#
# Наименование вакансии.
# Предлагаемую зарплату (отдельно минимальную и максимальную).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.

from bs4 import BeautifulSoup as bs
import requests
import re
import json
from pprint import pprint


def parse_salary(line):
    pattern1 = re.compile(r'(\d*\s\d*)\s–\s(\d*\s\d*)\s(.*)')
    pattern2 = re.compile(r'от\s(\d*\s\d*)\s(.*)')
    pattern3 = re.compile(r'до\s(\d*\s\d*)\s(.*)')
    salary = {}
    try:
        p_line = pattern1.match(line)
        if p_line:
            salary['from'] = int(p_line.groups()[0].replace('\u202f', ''))
            salary['to'] = int(p_line.groups()[1].replace('\u202f', ''))
            salary['currency'] = p_line.groups()[2]
            return salary
        p_line = pattern2.match(line)
        if p_line:
            salary['to'] = int(p_line.groups()[0].replace('\u202f', ''))
            salary['currency'] = p_line.groups()[1]
            return salary
        p_line = pattern3.match(line)
        if p_line:
            salary['from'] = int(p_line.groups()[0].replace('\u202f', ''))
            salary['currency'] = p_line.groups()[1]
            return salary
    except ValueError:
        print('Ошибка!!!')
    return salary


def save_vacancies(v_list):
    with open('vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(v_list, f, indent=4, ensure_ascii=False)


search_request = input('Введите название вакансии для поиска: ')
while True:
    try:
        max_page = int(input('Введите количество страниц: '))
        if max_page > 0:
            break
        else:
            print('Количество страниц должно быть положительным')
    except ValueError:
        print('Ошибка ввода')

url = 'https://hh.ru/search/vacancy'

params = {'area': '1',
          'st': 'searchVacancy',
          'text': search_request}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'}
page = 1

vacancies = []
while True:
    params['page'] = page
    try:
        response = requests.get(url, params=params, headers=headers)
    except OSError:
        print('Не удалось получить данные')
        break
    if response.status_code >= 300:
        print('Не удалось получить данные')
        break
    soup = bs(response.text, 'html.parser')
    vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    for vacancy in vacancy_list:
        vacancy_info = {}
        vacancy_header = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
        vacancy_name = vacancy_header.getText()
        vacancy_link = vacancy_header.get('href')
        vacancy_salary = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if vacancy_salary:
            vacancy_salary = parse_salary(vacancy_salary.getText())
        else:
            vacancy_salary = None
        vacancy_company = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).getText()

        vacancy_info['name'] = vacancy_name
        vacancy_info['link'] = vacancy_link
        vacancy_info['employer'] = vacancy_company
        vacancy_info['salary'] = vacancy_salary
        vacancy_info['source'] = 'HeadHunter'

        vacancies.append(vacancy_info)
    if soup.find('a', attrs={'data-qa': 'pager-next'}) and page < max_page:
        page += 1
    else:
        break

save_vacancies(vacancies)
pprint(vacancies)


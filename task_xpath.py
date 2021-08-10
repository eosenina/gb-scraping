# Задание 1.
# Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# Задание 2. Сложить собранные данные в БД
import locale

from lxml import html
import requests
from pprint import pprint
import datetime
from pymongo import MongoClient

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def collect_lenta_news():
    url = 'https://lenta.ru'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'}
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)
    news = dom.xpath('//time[@class="g-time"]/..')
    news_list = []
    for item in news:
        news_info = {}
        news_info['source'] = 'Lenta.ru'
        news_info['link'] = url + item.xpath('./@href')[0]
        news_info['title'] = item.xpath('./text()')[0].replace('\xa0', ' ')
        str_date = item.xpath('./time/@datetime')[0].replace(' ', '')
        news_info['date'] = datetime.datetime.strptime(str_date, '%H:%M,%d%B%Y')
        news_list.append(news_info)

    return news_list


def collect_mailru_news():
    url = 'https://news.mail.ru'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'}
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)
    links = dom.xpath("//div[@class='js-module']//@href")
    news_list = []
    for link in links:
        response = requests.get(link, headers=headers)
        dom = html.fromstring(response.text)
        news_info = {}
        news_info['title'] = dom.xpath('//h1/text()')[0]
        str_date = dom.xpath("//span[@class='note']/span/@datetime")[0][:-6:]
        news_info['date'] = datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S')
        news_info['link'] = link
        news_info['source'] = dom.xpath("//span[@class='note']/a/span/text()")[0]
        news_list.append(news_info)

    return news_list


client = MongoClient('localhost', 27017)
db = client['scraping_db']
collection = db.news_collection
news_list = collect_lenta_news()
news_list.extend(collect_mailru_news())
for item in news_list:
    collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
# pprint(news_list)

for item in collection.find({}):
    pprint(item)


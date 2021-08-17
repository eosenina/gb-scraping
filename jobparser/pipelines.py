# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client['vacancies_scrapy']

    def __parse_salary_hh(self, line):
        pattern1 = re.compile(r'от\s*(\d*)\s*до\s*(\d*)\s*(.*)')
        pattern2 = re.compile(r'от\s*(\d*)\s*(.*)')
        pattern3 = re.compile(r'до\s*(\d*)\s*(.*)')
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

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            sal_parsed = self.__parse_salary_hh(item['salary_from'].replace('\xa0', ''))
            item['salary_from'] = sal_parsed.get('from')
            item['salary_to'] = sal_parsed.get('to')
            item['salary_currency'] = sal_parsed.get('currency')
        if spider.name == 'sjru':
            pass
        item['site'] = spider.name
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

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
        patterns = {'full': re.compile(r'от\s*(\d*)\s*до\s*(\d*)\s*(.*)'),
                    'from': re.compile(r'от\s*(\d*)\s*(.*)'),
                    'to': re.compile(r'до\s*(\d*)\s*(.*)')
                    }
        return self.__try_salary_patterns(patterns, line)

    def __try_salary_patterns(self, pattern_dict, line):
        salary = {}
        try:
            p_line = pattern_dict['full'].match(line)
            if p_line:
                salary['from'] = int(p_line.groups()[0].replace('\u202f', ''))
                salary['to'] = int(p_line.groups()[1].replace('\u202f', ''))
                salary['currency'] = p_line.groups()[2]
                return salary
            p_line = pattern_dict['from'].match(line)
            if p_line:
                salary['from'] = int(p_line.groups()[0].replace('\u202f', ''))
                salary['currency'] = p_line.groups()[1]
                return salary
            p_line = pattern_dict['to'].match(line)
            if p_line:
                salary['to'] = int(p_line.groups()[0].replace('\u202f', ''))
                salary['currency'] = p_line.groups()[1]
                return salary
        except ValueError:
            print('Ошибка!!!')
        return salary

    def __parse_salary_sj(self, line):
        patterns = {'full': re.compile(r'от\s*(\d*)\s*до\s*(\d*)\s*(.*)/месяц'),
                    'from': re.compile(r'от\s*(\d*)\s*(.*)/месяц'),
                    'to': re.compile(r'до\s*(\d*)\s*(.*)/месяц')
                    }
        return self.__try_salary_patterns(patterns, line)

    def process_item(self, item, spider):
        sal_parsed = {}
        if spider.name == 'hhru':
            sal_parsed = self.__parse_salary_hh(item['salary_from'].replace('\xa0', ''))
        if spider.name == 'sjru':
            print()
            sal_line = ''.join(item['salary_from']).replace('\xa0', '')
            sal_parsed = self.__parse_salary_sj(sal_line)

        item['salary_from'] = sal_parsed.get('from')
        item['salary_to'] = sal_parsed.get('to')
        item['salary_currency'] = sal_parsed.get('currency')
        item['site'] = spider.name
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

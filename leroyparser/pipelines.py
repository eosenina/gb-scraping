# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class LeroyParserPipeline:
    def __init__(self):
         client = MongoClient('localhost', 27017)
         self.mongo_base = client['leroy_scrapy']

    def process_item(self, item, spider):
        item['price'] = item['price'][:2]
        item['spec'] = {key: val for key, val in zip(item['spec'][::2], item['spec'][1::2])}
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class LeroyPhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    # def file_path(self, request, response=None, info=None, *, item=None):
    #     pass

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

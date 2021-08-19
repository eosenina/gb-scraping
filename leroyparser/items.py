# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def convert_price(value):
    return int(value)


def parse_specifications(spec):
    pass


class LeroyParserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(convert_price))
    specifications = scrapy.Field(input_processor=MapCompose(parse_specifications))

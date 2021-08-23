import scrapy


class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']

    def parse(self, response):
        pass

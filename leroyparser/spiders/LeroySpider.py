import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from leroyparser.items import LeroyParserItem


class LeroySpider(scrapy.Spider):
    name = 'LeroyMerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru']

    def __init__(self, search):
        super(LeroySpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyParserItem(), response=response)
        loader.add_xpath("name", "//h1/text()")
        loader.add_xpath("photos", "//picture/img/@data-origin")
        loader.add_value("url", response.url)
        loader.add_xpath("spec", "//div[@class='def-list__group']/child::node()/text()")
        loader.add_xpath("price", "//span[@slot='price']/text() | //span[@slot='fract']/text()")

        yield loader.load_item()


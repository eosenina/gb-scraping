import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@class, 'f-test-link-Dalshe')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//div[contains(@class, 'f-test-vacancy-item')]//a[@target='_blank']/@href").extract()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        vac_name = response.xpath("//h1/text()").extract_first()
        vac_salary = response.xpath('//h1/following-sibling::span//text()').extract()
        vac_url = response.url
        yield JobparserItem(name=vac_name, salary_from=vac_salary, url=vac_url)

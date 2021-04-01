import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from minnwestbank.items import Article


class minnwestbankSpider(scrapy.Spider):
    name = 'minnwestbank'
    start_urls = ['https://www.minnwestbank.com/blog/tag/business?hsLang=en']

    def parse(self, response):
        links = response.xpath('//a[@class="post__link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@aria-label="Next Blog Listing Page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="blog-header-single-post__date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="blog-post__body"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

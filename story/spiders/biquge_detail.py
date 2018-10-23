# -*- coding: utf-8 -*-
import scrapy
from story.items import StoryDetailItem


class BiqugeSpider(scrapy.Spider):
    name = 'biquge_detail'
    allowed_domains = ['www.biquge.com.tw']
    start_urls = ['http://www.biquge.com.tw/20_20057/']

    def parse(self, response):

        docs = response.xpath('//div[@id="list"]/dl/dd')
        if len(docs) > 0:
            for doc in docs:
                item = StoryDetailItem()
                item['url'] = doc.xpath('./a/@href').extract_first()
                item['url'] = response.urljoin(item['url'])
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

    def parse_detail(self, response):

        item = response.meta['item']
        item['title'] = response.xpath('//div[@class="bookname"]/h1/text()').extract()[0]
        item['content'] = response.xpath('//div[@id="content"]').extract()[0]

        yield item

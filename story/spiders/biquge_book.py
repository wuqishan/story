# -*- coding: utf-8 -*-
import scrapy
from story.items import StoryItem


class BiqugeSpider(scrapy.Spider):
    name = 'biquge'
    allowed_domains = ['www.biquge.com.tw']
    start_urls = ['http://www.biquge.com.tw/xuanhuan/']

    def parse(self, response):

        # 顶部六篇
        docs = response.xpath('//div[@id="hotcontent"]/div[@class="ll"]/div[@class="item"]')
        if len(docs) > 0:
            for doc in docs:
                item = StoryItem()
                item['url'] = doc.xpath('./div[@class="image"]/a/@href').extract_first()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

        # 最近更新列表
        docs2 = response.xpath('//div[@id="newscontent"]/div[@class="l"]/ul/li')
        if len(docs2) > 0:
            for doc in docs2:
                item = StoryItem()
                item['url'] = doc.xpath('./span[@class="s2"]/a/@href').extract_first()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

        # 右侧好看的xx小说
        docs3 = response.xpath('//div[@id="newscontent"]/div[@class="r"]/ul/li')
        if len(docs3) > 0:
            for doc in docs3:
                item = StoryItem()
                item['url'] = doc.xpath('./span[@class="s2"]/a/@href').extract_first()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

    def parse_detail(self, response):

        item = response.meta['item']
        item['title'] = response.xpath('//div[@id="maininfo"]/div[@id="info"]/h1/text()').extract()[0]

        item['author'] = response.xpath('//div[@id="maininfo"]/div[@id="info"]/p[1]/text()').extract()[0]
        item['last_update'] = response.xpath('//div[@id="maininfo"]/div[@id="info"]/p[3]/text()').extract()
        if item['last_update']:
            item['last_update'] = item['last_update'][0]
        else:
            item['last_update'] = ""

        item['description'] = response.xpath('//div[@id="maininfo"]/div[@id="intro"]/p/text()').extract()
        if item['description']:
            item['description'] = item['description'][0]
        else:
            item['description'] = ""

        item['image'] = response.xpath('//div[@id="fmimg"]/img/@src').extract()
        if item['image']:
            item['image'] = item['image'][0]
        else:
            item['image'] = ""

        yield item

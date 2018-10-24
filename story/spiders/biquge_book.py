# -*- coding: utf-8 -*-
import scrapy
from story.items import StoryItem
import datetime
import re
import hashlib

class BiqugeSpider(scrapy.Spider):
    name = 'biquge'
    allowed_domains = ['www.biquge.com.tw']
    start_urls = ['http://www.biquge.com.tw/xuanhuan/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'story.pipelines.StoryPipeline': 300
        }
    }

    def parse(self, response):

        # 顶部六篇
        docs = response.xpath('//div[@id="hotcontent"]/div[@class="ll"]/div[@class="item"]')
        if len(docs) > 0:
            for doc in docs:
                item = StoryItem()
                item['url'] = doc.xpath('./div[@class="image"]/a/@href').extract_first()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

        # 最近更新列表
        # docs2 = response.xpath('//div[@id="newscontent"]/div[@class="l"]/ul/li')
        # if len(docs2) > 0:
        #     for doc in docs2:
        #         item = StoryItem()
        #         item['url'] = doc.xpath('./span[@class="s2"]/a/@href').extract_first()
        #         yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

        # 右侧好看的xx小说
        # docs3 = response.xpath('//div[@id="newscontent"]/div[@class="r"]/ul/li')
        # if len(docs3) > 0:
        #     for doc in docs3:
        #         item = StoryItem()
        #         item['url'] = doc.xpath('./span[@class="s2"]/a/@href').extract_first()
        #         yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

    def parse_detail(self, response):

        item = response.meta['item']
        item['title'] = response.xpath('//div[@id="maininfo"]/div[@id="info"]/h1/text()').extract()[0].strip()

        item['author'] = response.xpath('//div[@id="maininfo"]/div[@id="info"]/p[1]/text()').extract()[0].strip()
        item['last_update'] = response.xpath('//div[@id="maininfo"]/div[@id="info"]/p[3]/text()').extract()
        if item['last_update']:
            item['last_update'] = item['last_update'][0].strip()
        else:
            item['last_update'] = ""

        item['description'] = response.xpath('//div[@id="maininfo"]/div[@id="intro"]/p/text()').extract()
        if item['description']:
            item['description'] = item['description'][0].strip()
        else:
            item['description'] = ""

        item['image'] = response.xpath('//div[@id="fmimg"]/img/@src').extract()
        if item['image']:
            item['image'] = response.urljoin(item['image'][0].strip())
        else:
            item['image'] = ""

        # 处理item
        item['author'] = re.sub(r'作(\s|(&nbsp;))*?者(：|\:)', '', item['author'], flags=re.I)
        item['last_update'] = re.sub(r'[\u4E00-\u9FA5]*(：|\:)', '', item['last_update'], flags=re.I)
        item['unique_code'] = self.get_md5(item['title'] + item['author'])
        item['created_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        yield item

    def get_md5(self, string):
        m = hashlib.md5()
        m.update(string.encode("utf8"))
        return m.hexdigest()
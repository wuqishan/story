# -*- coding: utf-8 -*-
import scrapy
from story.items import StoryItem
import datetime
import re
from story.tools import *
from story.mysql import mysql_helper

class BiqugeSpider(scrapy.Spider):
    name = 'biquge'
    allowed_domains = ['www.biquge.com.tw']
    start_urls = [
        'http://www.biquge.com.tw/xuanhuan/',
        'http://www.biquge.com.tw/xiuzhen/',
        'http://www.biquge.com.tw/dushi/',
        'http://www.biquge.com.tw/lishi/',
        'http://www.biquge.com.tw/wangyou/',
        'http://www.biquge.com.tw/kehuan/',
        'http://www.biquge.com.tw/kongbu/',
        'http://www.biquge.com.tw/quanben/',
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'story.pipelines.ImagesDownloadPipeline': 5,
            'story.pipelines.StoryPipeline': 300,
        }
    }

    def parse(self, response):

        # 顶部六篇
        docs = response.xpath('//div[@id="hotcontent"]/div[@class="ll"]/div[@class="item"]')
        if len(docs) > 0:
            for doc in docs:
                item = StoryItem()
                item['category_id'] = self.start_urls.index(response.url)
                item['url'] = doc.xpath('./div[@class="image"]/a/@href').extract_first()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

        # 最近更新列表
        docs2 = response.xpath('//div[@id="newscontent"]/div[@class="l"]/ul/li')
        if len(docs2) > 0:
            for doc in docs2:
                item = StoryItem()
                item['category_id'] = self.start_urls.index(response.url)
                item['url'] = doc.xpath('./span[@class="s2"]/a/@href').extract_first()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

        # 右侧好看的xx小说
        docs3 = response.xpath('//div[@id="newscontent"]/div[@class="r"]/ul/li')
        if len(docs3) > 0:
            for doc in docs3:
                item = StoryItem()
                item['category_id'] = self.start_urls.index(response.url)
                item['url'] = doc.xpath('./span[@class="s2"]/a/@href').extract_first()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

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

        item['image_origin_url'] = response.xpath('//div[@id="fmimg"]/img/@src').extract()
        if item['image_origin_url']:
            item['image_origin_url'] = response.urljoin(item['image_origin_url'][0].strip())
        else:
            item['image_origin_url'] = ''

        # 处理item
        item['image_local_url'] = ''
        item['author'] = re.sub(r'作(\s|(&nbsp;))*?者(：|\:)', '', item['author'])
        item['author_id'] = self.get_author_id(item['author'])
        item['last_update'] = re.sub(r'[\u4E00-\u9FA5]*(：|\:)', '', item['last_update'], flags=re.I)
        item['unique_code'] = get_md5(item['author'] + item['title'])
        item['created_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        yield item

    # 获取作者id
    def get_author_id(self, author_name):
        author_sql = "select id from bqg_author where name = %s"
        author_params = author_name
        results = mysql_helper.get_instance().get_one(author_sql, author_params)

        if results is None:
            insert_author_sql = "insert into bqg_author(name) values (%s)"
            insert_author_params = author_name
            mysql_helper.get_instance().insert(insert_author_sql, insert_author_params)
            results = mysql_helper.get_instance().get_one(author_sql, author_params)

        return results['id']
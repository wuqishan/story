# -*- coding: utf-8 -*-
import scrapy
from story.items import StoryDetailItem
import re
import hashlib
import datetime

class BiqugeSpider(scrapy.Spider):
    name = 'biquge_detail'
    allowed_domains = ['www.biquge.com.tw']

    start_urls = [
        'http://www.biquge.com.tw/xuanhuan/',
        # 'http://www.biquge.com.tw/xiuzhen/',
        # 'http://www.biquge.com.tw/dushi/',
        # 'http://www.biquge.com.tw/lishi/',
        # 'http://www.biquge.com.tw/wangyou/',
        # 'http://www.biquge.com.tw/kehuan/',
        # 'http://www.biquge.com.tw/kongbu/'
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'story.pipelines.StoryDetailPipeline': 300
        }
    }

    # 这里先获取每一本书的url，然后根据每一本书的url去获取章节信息
    def parse(self, response):
        # 顶部六篇
        docs = response.xpath('//div[@id="hotcontent"]/div[@class="ll"]/div[@class="item"]')
        if len(docs) > 0:
            for doc in docs:
                url = doc.xpath('./div[@class="image"]/a/@href').extract_first().strip()
                yield scrapy.Request(url, callback=self.parse_chapter)

        # 最近更新列表
        # docs2 = response.xpath('//div[@id="newscontent"]/div[@class="l"]/ul/li')
        # if len(docs2) > 0:
        #     for doc in docs2:
        #         url = doc.xpath('./span[@class="s2"]/a/@href').extract_first().strip()
        #         yield scrapy.Request(url, callback=self.parse_chapter)

        # 右侧好看的xx小说
        # docs3 = response.xpath('//div[@id="newscontent"]/div[@class="r"]/ul/li')
        # if len(docs3) > 0:
        #     for doc in docs3:
        #         url = doc.xpath('./span[@class="s2"]/a/@href').extract_first().strip()
        #         yield scrapy.Request(url, callback=self.parse_chapter)

    def parse_chapter(self, response):

        docs = response.xpath('//div[@id="list"]/dl/dd')
        book_title = response.xpath('//div[@id="info"]/h1/text()').extract_first().strip()
        book_author = response.xpath('//div[@id="info"]/p[1]/text()').extract_first().strip()
        book_author = re.sub(r'作(\s|(&nbsp;))*?者(：|\:)', '', book_author)

        if len(docs) > 0:

            for i, doc in enumerate(docs):
                item = StoryDetailItem()
                item['title'] = doc.xpath('./a/text()').extract_first().strip()
                item['url'] = doc.xpath('./a/@href').extract_first()
                item['url'] = response.urljoin(item['url'])
                item['book_unique_code'] = self.get_md5(book_author + book_title)
                item['unique_code'] = self.get_md5(book_author + book_title + item['title'])
                item['orderby'] = i

                if i == 0 and len(docs) == 1:
                    item['prev_unique_code'] = ''
                    item['next_unique_code'] = ''
                elif i == 0 and len(docs) > 1:
                    item['prev_unique_code'] = ''
                    next_title = docs[i + 1].xpath('./a/text()').extract_first().strip()
                    item['next_unique_code'] = self.get_md5(book_author + book_title + next_title)
                elif i == len(docs) - 1:
                    prev_title = docs[i - 1].xpath('./a/text()').extract_first().strip()
                    item['prev_unique_code'] = self.get_md5(book_author + book_title + prev_title)
                    item['next_unique_code'] = ''
                else:
                    next_title = docs[i + 1].xpath('./a/text()').extract_first().strip()
                    prev_title = docs[i - 1].xpath('./a/text()').extract_first().strip()
                    item['next_unique_code'] = self.get_md5(book_author + book_title + next_title)
                    item['prev_unique_code'] = self.get_md5(book_author + book_title + prev_title)

                item['created_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                item['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

    def parse_detail(self, response):

        item = response.meta['item']
        item['content'] = response.xpath('//div[@id="content"]').extract_first().strip()

        yield item

    def get_md5(self, string):
        m = hashlib.md5()
        m.update(string.encode("utf8"))
        return m.hexdigest()

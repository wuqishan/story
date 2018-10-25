# -*- coding: utf-8 -*-
import scrapy
from story.items import StoryDetailItem
import re
import datetime
from story.mysql import mysql_helper
from story.tools import *


class BiqugeSpider(scrapy.Spider):
    name = 'biquge_detail'
    allowed_domains = ['www.biquge.com.tw']

    # 在方法 get_start_urls 从数据库中取
    start_urls = []

    custom_settings = {
        'ITEM_PIPELINES': {
            'story.pipelines.StoryDetailPipeline': 300
        }
    }

    def start_requests(self):
        start_urls = self.get_start_urls()
        # start_urls = [{'url': 'http://www.biquge.com.tw/20_20022/'}]
        if start_urls:
            for val in start_urls:
                yield scrapy.Request(val['url'], callback=self.parse_chapter)

    def get_start_urls(self):
        sql = "select url from bqg_book where finished = 0"
        resutls = mysql_helper.get_instance().get_all(sql)

        return resutls

    def parse_chapter(self, response):

        docs = response.xpath('//div[@id="list"]/dl/dd')
        book_title = response.xpath('//div[@id="info"]/h1/text()').extract_first().strip()
        book_author = response.xpath('//div[@id="info"]/p[1]/text()').extract_first().strip()
        book_author = re.sub(r'作(\s|(&nbsp;))*?者(：|\:)', '', book_author)

        run_at = None
        if len(docs) > 0:
            for i, doc in enumerate(docs):
                item = StoryDetailItem()
                item['title'] = doc.xpath('./a/text()').extract_first().strip()
                item['url'] = doc.xpath('./a/@href').extract_first()
                item['url'] = response.urljoin(item['url'])
                item['book_unique_code'] = get_md5(book_author + book_title)
                item['unique_code'] = get_md5(book_author + book_title + item['title'])
                item['orderby'] = i

                if i == 0 and len(docs) == 1:
                    item['prev_unique_code'] = ''
                    item['next_unique_code'] = ''
                elif i == 0 and len(docs) > 1:
                    item['prev_unique_code'] = ''
                    next_title = docs[i + 1].xpath('./a/text()').extract_first().strip()
                    item['next_unique_code'] = get_md5(book_author + book_title + next_title)
                elif i == len(docs) - 1:
                    prev_title = docs[i - 1].xpath('./a/text()').extract_first().strip()
                    item['prev_unique_code'] = get_md5(book_author + book_title + prev_title)
                    item['next_unique_code'] = ''
                else:
                    next_title = docs[i + 1].xpath('./a/text()').extract_first().strip()
                    prev_title = docs[i - 1].xpath('./a/text()').extract_first().strip()
                    item['next_unique_code'] = get_md5(book_author + book_title + next_title)
                    item['prev_unique_code'] = get_md5(book_author + book_title + prev_title)

                item['created_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                item['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # run_at 函数每个url只执行一次，后面就更具orderby进行跳过了
                if run_at is None:
                    run_at = self.run_at(item)
                elif run_at > i:
                    continue

                # 如果已经有了则不做处理
                # if self.check_has(item):
                #     continue

                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.parse_detail)

    def parse_detail(self, response):

        item = response.meta['item']
        item['content'] = response.xpath('//div[@id="content"]').extract_first().strip()

        yield item

    # 如果当前章节没有入库并且有上一章记录,则更新上条记录的 next_unique_code 值，并返回False，否则返回True
    def check_has(self, item):
        status = True
        sql = "select id from bqg_chapter where unique_code = %s"
        params = item['unique_code']
        result = mysql_helper.get_instance().get_one(sql, params)
        if result is None:
            status = False
            if item['prev_unique_code'] != "":
                update_sql = "update bqg_chapter set next_unique_code = %s where unique_code = %s"
                update_params = (item['unique_code'], item['prev_unique_code'])
                mysql_helper.get_instance().update(update_sql, update_params)

        return status

    # 获取从哪里开始继续抓取
    def run_at(self, item):
        orderby = 0
        sql = "select id from bqg_chapter order by orderby desc where book_unique_code = %s limit 1"
        params = item['book_unique_code']
        result = mysql_helper.get_instance().get_one(sql, params)
        if result:
            orderby = result['orderby']
            if item['next_unique_code'] != "":
                update_sql = "update bqg_chapter set next_unique_code = %s where unique_code = %s"
                update_params = (item['next_unique_code'], item['unique_code'])
                mysql_helper.get_instance().update(update_sql, update_params)

        return orderby
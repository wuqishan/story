# -*- coding: utf-8 -*-
import scrapy


class BiqugeSpider(scrapy.Spider):
    name = 'biquge'
    allowed_domains = ['www.biquge.com.tw/xuanhuan/']
    start_urls = ['http://www.biquge.com.tw/xuanhuan//']

    def parse(self, response):
        pass

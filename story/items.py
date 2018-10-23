# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class StoryItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()          # 标题
    author = scrapy.Field()         # 作者
    last_update = scrapy.Field()    # 最后更新时间
    description = scrapy.Field()    # 描述
    image = scrapy.Field()          # 图片地址
    url = scrapy.Field()            # 小说url


class StoryDetailItem(scrapy.Item):
    title = scrapy.Field()          # 标题
    content = scrapy.Field()        # 内容
    url = scrapy.Field()            # 小说url
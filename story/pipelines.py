# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import pymysql
import pymysql.cursors
from scrapy.exceptions import DropItem
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from story.settings import IMAGES_STORE
from story.tools import *

class StoryPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.new_item = []

    @classmethod
    def from_settings(cls, settings):
        dbpool = adbapi.ConnectionPool("pymysql", host=settings["MYSQL_HOST"], db=settings["MYSQL_DBNAME"],
                                       user=settings["MYSQL_USER"], password=settings["MYSQL_PASSWORD"],
                                       charset="utf8mb4",
                                       cursorclass=pymysql.cursors.DictCursor,
                                       use_unicode=True)
        return cls(dbpool)

    def process_item(self, item, spider):

        if not item['title'] or not item['author'] or not item['url']:
            raise DropItem("Missing title|author|url in {}".format(item))
        else:
            self.dbpool.runInteraction(self.db_logic, item)

    def close_spider(self, spider):
        sendmail(spider.settings, 1, self.new_item)

    # 数据库更新逻辑
    def db_logic(self, cursor, item):
        check_sql, check_params = item.get_check_sql()
        cursor.execute(check_sql, check_params)
        results = cursor.fetchone()
        # 如果不存在该记录 or 该本书还未完本
        if results is None or results['finished'] != 0:
            # 如果不存在该记录则插入，如果存在该记录则更新最近更新时间
            if results is None:
                self.new_item.append({
                    'title': item['title'],
                    'author': item['author'],
                    'url': item['url'],
                    'unique_code': item['unique_code']
                })
                insert_sql, insert_params = item.get_insert_sql()
                cursor.execute(insert_sql, insert_params)
            else:
                update_sql, update_params = item.get_update_sql()
                cursor.execute(update_sql, update_params)


class StoryDetailPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.new_item = []

    @classmethod
    def from_settings(cls, settings):
        dbpool = adbapi.ConnectionPool("pymysql", host=settings["MYSQL_HOST"], db=settings["MYSQL_DBNAME"],
                                       user=settings["MYSQL_USER"], password=settings["MYSQL_PASSWORD"],
                                       charset="utf8mb4",
                                       cursorclass=pymysql.cursors.DictCursor,
                                       use_unicode=True)
        return cls(dbpool)

    def process_item(self, item, spider):

        if not item['title'] or not item['content'] or not item['url']:
            raise DropItem("Missing title|content|url in {}".format(item))
        else:
            self.dbpool.runInteraction(self.db_logic, item)

    # 检测当前章节是否已经存在，在爬取地方已经检测过了，这里就不做了
    def db_logic(self, cursor, item):
        # check_sql, check_params = item.get_check_sql()
        # cursor.execute(check_sql, check_params)
        # results = cursor.fetchone()
        # if results is None:
        self.new_item.append({
            'title': item['title'],
            'url': item['url'],
            'unique_code': item['unique_code'],
            'book_unique_code': item['book_unique_code'],
        })

        insert_sql, insert_params = item.get_insert_sql()
        cursor.execute(insert_sql, insert_params)

    def close_spider(self, spider):
        sendmail(spider.settings, 2, self.new_item)


class ImagesDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['image_origin_url'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            item['image_local_url'] = ''
        else:
            item['image_local_url'] = IMAGES_STORE + image_paths[0]

        return item

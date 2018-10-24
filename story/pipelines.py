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


class StoryPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        # config = {
        #     "host": settings["MYSQL_HOST"],
        #     "port": 3306,
        #     "database": settings["MYSQL_DBNAME"],
        #     "user": settings["MYSQL_USER"],
        #     "password": settings["MYSQL_PASSWORD"],
        #     "charset": "utf8mb4",
        #     "cursorclass": pymysql.cursors.DictCursor,
        #     "use_unicode": True
        # }
        # self.conn = pymysql.connect(**config)
        # conn.ping()
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
            # 使用twisted将mysql插入变成异步执行
            self.dbpool.runInteraction(self.db_logic, item)

    def close_spider(self, spider):
        pass

    def db_logic(self, cursor, item):
        '''
        数据库更新逻辑
        '''
        check_sql, check_params = item.get_check_sql()
        cursor.execute(check_sql, check_params)
        results = cursor.fetchone()

        # 如果不存在该记录 or 该本书还未完本
        if results is None or results['finished'] != 0:
            # 如果不存在该记录则插入，如果存在该记录则更新最近更新时间
            if results is None:
                author_sql, author_params = item.get_author_sql()
                cursor.execute(author_sql, author_params)
                author = cursor.fetchone()
                if author is None:
                    insert_author_sql, insert_author_params = item.get_insert_author_sql()
                    cursor.execute(insert_author_sql, insert_author_params)
                    cursor.execute(author_sql, author_params)
                    author = cursor.fetchone()

                item['author_id'] = author['id']
                item['description'] = "abc"
                insert_sql, insert_params = item.get_insert_sql()
                cursor.execute(insert_sql, insert_params)
            else:
                update_sql, update_params = item.get_update_sql()
                cursor.execute(update_sql, update_params)


class StoryDetailPipeline(object):
    def __init__(self, connect, cursor):
        self.connect = connect
        self.cursor = cursor

    @classmethod
    def from_settings(cls, settings):
        config = {
            "host": settings["MYSQL_HOST"],
            "port": 3306,
            "database": settings["MYSQL_DBNAME"],
            "user": settings["MYSQL_USER"],
            "password": settings["MYSQL_PASSWORD"],
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
            "use_unicode": True
        }
        connect = pymysql.connect(**config)
        cursor = connect.cursor()
        # dbpool = adbapi.ConnectionPool("pymysql", host=settings["MYSQL_HOST"], db=settings["MYSQL_DBNAME"],
        #                                user=settings["MYSQL_USER"], password=settings["MYSQL_PASSWORD"],
        #                                charset="utf8mb4",
        #                                cursorclass=pymysql.cursors.DictCursor,
        #                                use_unicode=True)

        return cls(cursor, cursor)

    def process_item(self, item, spider):

        if not item['title'] or not item['content'] or not item['url']:
            raise DropItem("Missing title|content|url in {}".format(item))
        else:
            # 使用twisted将mysql插入变成异步执行
            self.db_logic(item)

    def db_logic(self, item):
        '''
        数据库更新逻辑
        '''
        self.connect.ping()
        check_sql, check_params = item.get_check_sql()
        self.cursor.execute(check_sql, check_params)
        results = self.cursor.fetchone()

        # 如果不存在该记录则插入，如果存在该记录则更新最近更新时间
        if results is None:
            insert_sql, insert_params = item.get_insert_sql()
            self.cursor.execute(insert_sql, insert_params)
            self.connect.commit()

                # self.cursor.execute(insert_sql, insert_params)
                # self.connect.commit()

    def close_spider(self, spider):
        self.connect.close()


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

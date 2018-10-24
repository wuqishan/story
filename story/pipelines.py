# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import pymysql
import pymysql.cursors


class StoryPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbpool = adbapi.ConnectionPool("pymysql", host=settings["MYSQL_HOST"], db=settings["MYSQL_DBNAME"],
                                       user=settings["MYSQL_USER"], password=settings["MYSQL_PASSWORD"],
                                       charset="utf8mb4",
                                       cursorclass=pymysql.cursors.DictCursor,
                                       use_unicode=True)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        self.dbpool.runInteraction(self.db_logic, item)

        # yield item

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
                insert_sql, insert_params = item.get_insert_sql()
                cursor.execute(insert_sql, insert_params)
            else:
                update_sql, update_params = item.get_update_sql()
                cursor.execute(update_sql, update_params)

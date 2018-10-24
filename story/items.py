# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class StoryItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()  # 标题
    author = scrapy.Field()  # 作者
    last_update = scrapy.Field()  # 最后更新时间
    description = scrapy.Field()  # 描述
    image_local_url = scrapy.Field()  # 图片地址
    image_origin_url = scrapy.Field()  # 图片地址
    url = scrapy.Field()  # 小说url

    unique_code = scrapy.Field()  # 辅助字段
    created_at = scrapy.Field()  # 辅助字段
    updated_at = scrapy.Field()  # 辅助字段

    def get_insert_sql(self):
        """
        插入数据的sql
        """
        insert_sql = """
        insert into bqg_book(unique_code, title, author, last_update, 
        description, image_local_url, image_origin_url, url, created_at, updated_at) 
        values 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        insert_params = (
            self['unique_code'], self['title'], self['author'], self['last_update'], self['description'],
            self['image_local_url'], self['image_origin_url'], self['url'], self['created_at'], self['updated_at'],
        )
        return insert_sql, insert_params

    def get_check_sql(self):
        """
        查询一条数据的sql，用于检查
        """
        check_sql = "select id, finished from bqg_book where unique_code = %s"
        check_params = (self['unique_code'])

        return check_sql, check_params

    def get_update_sql(self):
        """
        更新最近更新时间的sql
        """
        update_sql = "update bqg_book set last_update = %s, updated_at = %s where unique_code = %s"
        update_params = (self['last_update'], self['updated_at'], self['unique_code'])

        return update_sql, update_params


class StoryDetailItem(scrapy.Item):
    title = scrapy.Field()  # 标题
    content = scrapy.Field()  # 内容
    url = scrapy.Field()  # 小说url

    book_unique_code = scrapy.Field()  # 章节所属书的唯一码
    unique_code = scrapy.Field()  # 本章节唯一码
    prev_unique_code = scrapy.Field()  # 上一页章节唯一吗
    next_unique_code = scrapy.Field()  # 下一页章节唯一吗
    created_at = scrapy.Field()  # 创建时间
    updated_at = scrapy.Field()  # 更新时间

    def get_insert_sql(self):
        """
        插入数据的sql
        """
        insert_sql = """
        insert into bqg_chapter(book_unique_code, unique_code, prev_unique_code, next_unique_code, 
        title, content, view, created_at, updated_at) 
        values 
        (%s, %s, %s, %s, %s, %s, 0, %s, %s)"""

        insert_params = (
            self['book_unique_code'], self['unique_code'], self['prev_unique_code'], self['next_unique_code'],
            self['title'], self['content'], self['created_at'], self['updated_at'],
        )
        return insert_sql, insert_params

    def get_check_sql(self):
        """
        查询一条数据的sql，用于检查
        """
        check_sql = "select id from bqg_chapter where unique_code = %s"
        check_params = (self['unique_code'])

        return check_sql, check_params

    def get_update_sql(self):
        """
        更新最近更新时间的sql
        """
        update_sql = "update bqg_chapter set updated_at = %s where unique_code = %s"
        update_params = (self['updated_at'], self['unique_code'])

        return update_sql, update_params

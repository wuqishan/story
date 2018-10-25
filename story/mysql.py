import pymysql
import pymysql.cursors
from story.settings import *


class mysql_helper:
    __instance = None

    def __init__(self):
        config = {
            'host': MYSQL_HOST,
            'port': 3306,
            'user': MYSQL_USER,
            'passwd': MYSQL_PASSWORD,
            'db': MYSQL_DBNAME,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
            'use_unicode': True,
        }
        self.db = pymysql.Connect(**config)
        self.cursor = self.db.cursor()

    @classmethod  # 调用类的方法来创建一个单例
    def get_instance(cls):
        if cls.__instance:
            return cls.__instance
        else:
            cls.__instance = mysql_helper()
            return cls.__instance

    # 关闭链接
    # def close(self):
    #     self.cursor.close()
    #     self.db.close()

    # 查询单行记录
    def get_one(self, sql, params=None):
        self.db.ping()
        self.cursor.execute(sql, params)
        res = self.cursor.fetchone()

        return res

    # 查询列表数据
    def get_all(self, sql, params=None):
        self.db.ping()
        self.cursor.execute(sql, params)
        res = self.cursor.fetchall()

        return res

    # 插入数据
    def insert(self, sql, params=None):
        count = 0
        self.db.ping()
        try:
            count = self.cursor.execute(sql, params)
            self.db.commit()
        except:
            self.db.rollback()

        return count

    # 删除数据
    def delete(self, sql, params=None):
        return self.insert(sql, params)

    # 更新数据
    def update(self, sql, params=None):
        return self.insert(sql, params)

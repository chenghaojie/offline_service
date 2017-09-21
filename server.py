# -*- coding: utf-8 -*-
"""
服务启动
"""
from time import sleep

import pymongo
from mecloud.helper.DbHelper import Db
from lib.config import MongoDbConfig
from handler.face_cal import insert_data_to_queue


if __name__ == '__main__':
    Db.name = MongoDbConfig.NAME
    Db.conn = pymongo.MongoClient(MongoDbConfig.HOST, MongoDbConfig.PORT)
    Db.conn.admin.authenticate(MongoDbConfig.USER, MongoDbConfig.PASSWORD)
    while True:
        insert_data_to_queue()
        sleep(10)

# -*- coding: utf-8 -*-
"""
服务启动
"""
from time import sleep

import pymongo
from mecloud.helper.DbHelper import Db
from lib.config import MongoDbConfig
from handler.face_cal import start_face_cal


if __name__ == '__main__':
    Db.name = MongoDbConfig.NAME
    Db.conn = pymongo.MongoClient(MongoDbConfig.HOST, MongoDbConfig.PORT)
    Db.conn.admin.authenticate(MongoDbConfig.USER, MongoDbConfig.PASSWORD)
    num = 0
    while num < 10:
        num += 1
        print num
        sleep(5)
    # start_face_cal()

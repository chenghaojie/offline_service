# -*- coding: utf-8 -*-
"""
服务启动
"""

from time import sleep

from handler.face_cal import insert_data_to_queue


if __name__ == '__main__':
    while True:
        insert_data_to_queue()
        # 每隔10秒钟跑一次
        sleep(10)


# -*- coding: utf-8 -*-
"""
计算人脸向量相关
"""
import json

import datetime

import pymongo
import requests
from mecloud.helper.DbHelper import Db
from mecloud.helper.RedisHelper import RedisDb
from mecloud.helper.ClassHelper import ClassHelper

from lib import log
from lib.config import MongoDbConfig

LAST_CAL_ID_EXPIRE_TIME = 3600 * 24 * 30    # 缓存一个月,应该够了吧
MEDIA_COUNT_LIMIT = 1000    # 每次从数据库获取的media数量
MEDIA_COUNT_THRESHOLD = 50  # 当缓存数量小于阈值时再次获取

FEATURE_URL = "http://g00.me-yun.com:8001/local/feature?path=/tmp/renrenimg0724/%s.jpg"    # 人脸特征计算接口url

Db.name = MongoDbConfig.NAME
Db.conn = pymongo.MongoClient(MongoDbConfig.HOST, MongoDbConfig.PORT)
Db.conn.admin.authenticate(MongoDbConfig.USER, MongoDbConfig.PASSWORD)


def _build_last_cal_id_redis_key():
    """
    构造redis key
    :return:
    """
    return 'last_cal_id_key_20170921'


def get_last_cal_id():
    """
    获取上一次计算的最后一条数据的id
    :return:
    """
    client = RedisDb.get_connection()
    redis_key = _build_last_cal_id_redis_key()
    last_id = client.get(redis_key)
    return last_id


def set_last_cal_id(last_id):
    """
    保存上一次计算的最后一条数据的id
    :param last_id
    :return:
    """
    client = RedisDb.get_connection()
    redis_key = _build_last_cal_id_redis_key()
    client.setex(redis_key, last_id, LAST_CAL_ID_EXPIRE_TIME)


def get_media_id_list_from_db():
    """
    从db中获取media_id列表
    :return:
    """
    last_id = get_last_cal_id() or None
    media_helper = ClassHelper('Media')
    query = {'faces': {'$exists': False}}
    if last_id:
        query['_id'] = {'$gt': last_id}
    medias = media_helper.find(query=query, keys={"_id": 1}, sort=[("_id", 1)], limit=MEDIA_COUNT_LIMIT)
    media_id_list = []
    for media in medias:
        media_id_list.append(media['_id'])
    return media_id_list


def _build_media_redis_key():
    """
    构造redis key
    :return:
    """
    return 'media_key_20170921'


def save_media_to_redis(media_ids):
    """
    保存图片到redis中
    :return:
    :param media_ids
    """
    client = RedisDb.get_connection(dbid=1)
    redis_key = _build_media_redis_key()
    for media_id in media_ids:
        client.rpush(redis_key, media_id)


def get_media_count_from_redis():
    """
    从redis中获取media数量
    :return:
    """
    client = RedisDb.get_connection(dbid=1)
    redis_key = _build_media_redis_key()
    return client.llen(redis_key) or 0


def get_faces_from_media_id(media_id):
    """
    根据图片id计算出其中的人脸的特征向量
    通过http请求
    :param media_id:
    :return:
    """
    url = FEATURE_URL % media_id
    res = requests.get(url)
    data = json.loads(res.text)
    error_msg = data.get('errMsg')
    if error_msg:
        log.err('media %s calculate error: %s' % (media_id, error_msg))
        return []
    faces = data['facer']
    if not faces:
        log.info('media without faces: %s' % media_id)
    return faces


def create_face_db(face_info):
    """
    创建数据库face记录
    :param face_info:
    :return:
    """
    face_helper = ClassHelper('Face')
    now = datetime.datetime.now()
    face_info['createAt'] = face_info['updateAt'] = now
    face_info['acl'] = {
        '*': {
            "read": True,
            "write": True
        }
    }
    return face_helper.create(face_info)


def start_face_cal():
    """
    开始计算人脸向量
    :return:
    """
    media_helper = ClassHelper('Media')
    client = RedisDb.get_connection(dbid=1)
    redis_key = _build_media_redis_key()
    while client.llen(redis_key):
        media_id = client.lpop(redis_key)
        media = media_helper.get(media_id)
        if not media:
            log.err('media not found: %s' % media_id)
            continue
        faces = get_faces_from_media_id(media_id)
        face_ids = []
        for face_info in faces:
            face_info['media'] = media_id
            face = create_face_db(face_info)
            face_ids.append(face['_id'])
        # 没有获取到的话就不更新了
        if face_ids:
            media_helper.update(media_id, {'$set': {'faces': face_ids}})
            log.info('media face calculate finish: %s' % media_id)


def insert_data_to_queue():
    """
    往队列里添加数据
    :return:
    """
    left_media_count = get_media_count_from_redis()
    if left_media_count < MEDIA_COUNT_THRESHOLD:
        media_ids = get_media_id_list_from_db()
        if not media_ids:
            return
        save_media_to_redis(media_ids)
        last_cal_id = media_ids[-1]
        set_last_cal_id(last_cal_id)

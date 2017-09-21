# -*- coding: utf-8 -*-
"""
计算人脸向量相关
"""

from mecloud.helper.RedisHelper import RedisDb
from mecloud.helper.ClassHelper import *


LAST_CAL_ID_EXPIRE_TIME = 3600 * 24 * 30    # 缓存一个月,应该够了吧
MEDIA_COUNT_LIMIT = 1000
MEDIA_COUNT_THRESHOLD = 50

IMAGE_URL = "http://renrenimg0724.oss-cn-beijing.aliyuncs.com/{0}.{1}"
FEATURE_URL = "http://g00.me-yun.com:8001/local/feature?path=/tmp/renrenimg0724/{0}.{1}"


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
    medias = media_helper.find(query=query, keys={"_id": 1}, sort={"_id": 1}, limit=MEDIA_COUNT_LIMIT)
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


def insert_data_to_queue():
    """
    往队列里添加数据
    :return:
    """
    left_media_count = get_media_count_from_redis()
    if not left_media_count or left_media_count < MEDIA_COUNT_THRESHOLD:
        media_ids = get_media_id_list_from_db()
        save_media_to_redis(media_ids)
        last_cal_id = media_ids[-1]
        set_last_cal_id(last_cal_id)


def start_face_cal():
    """
    开始计算人脸向量
    :return:
    """
    media_helper = ClassHelper('Media')
    client = RedisDb.get_connection()
    redis_key = _build_media_redis_key()
    while client.llen(redis_key):
        media_id = client.lpop(redis_key)
        media = media_helper.get(media_id)
        print media
        pass


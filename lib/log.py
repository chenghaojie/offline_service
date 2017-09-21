# -*- coding: utf-8 -*-
"""
日志记录
"""
import datetime
import sys


def now_str():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f%Z')


def debug(format, *args, **kwargs):
    prefix = '[debug]' + now_str() + ': '
    print prefix + (format % args)
    sys.stdout.flush()


def info(format, *args, **kwargs):
    prefix = '[info]' + now_str() + ': '
    print prefix + (format % args)
    sys.stdout.flush()


def warn(format, *args, **kwargs):
    prefix = '[warn]' + now_str() + ': '
    print prefix + (format % args)
    sys.stdout.flush()


def err(format, *args, **kwargs):
    prefix = '[err]' + now_str() + ': '
    print prefix + (format % args)
    sys.stdout.flush()

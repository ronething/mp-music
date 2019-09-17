# -*- coding:utf-8 _*-
""" 
@author: ronething 
@time: 2019-04-02 00:56 
@mail: axingfly@gmail.com

Less is more.
"""

import os
import configparser

import xml.etree.cElementTree as et

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_mes(xml_data):
    xml_source = et.fromstring(xml_data)

    msg_type = xml_source.find('MsgType').text
    from_user = xml_source.find('FromUserName').text
    to_user = xml_source.find('ToUserName').text

    if msg_type == 'text':
        content = xml_source.find('Content').text
        return dict(
            type='text',
            to_user=to_user,
            from_user=from_user,
            content=content,
        )
    else:
        return dict(
            type='other',
            to_user=to_user,
            from_user=from_user,
        )


def get_redis_config():
    redis_config = configparser.ConfigParser()
    filename = os.path.join(BASE_DIR,"config","redis.conf")
    redis_config.read(filename)
    return redis_config

if __name__ == "__main__":
    get_redis_config()
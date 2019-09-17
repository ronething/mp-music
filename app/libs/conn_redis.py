# coding=utf-8

import redis

import json
import pickle
from json import JSONDecodeError


class ConnRedis(object):

    def __init__(self, config=None):
        self.__pool = redis.ConnectionPool(host=config.get('redis_db', 'host'), port=config.getint(
            'redis_db', 'port'), db=config.getint('redis_db', 'db'), password=config.get('redis_db', 'password'))
        self.redis_cli = redis.StrictRedis(connection_pool=self.__pool)

    def set_value(self, key: str, value: str, expire: int = 300) -> bool:
        if key is not None and key != '':
            self.redis_cli.set(key, value, ex=expire)
            return True
        else:
            return False

    def get_value(self, key: str) -> str:
        result = self.redis_cli.get(key)
        if result is not None:
            return result.decode()
        else:
            return None

    def set_dict(self, key: str, value: dict, expire: int = 300) -> bool:
        value = json.dumps(value, ensure_ascii=False)
        return self.set_value(key, value, expire)

    def get_dict(self, key: str) -> dict:
        try:
            result = self.get_value(key)
            if result is not None:
                result = json.loads(result)
            return result
        except TypeError:
            return None
        except JSONDecodeError:
            return None

    def set_list(self, key: str, value: list, expire: int = 300) -> bool:
        value = pickle.dumps(value)
        return self.set_value(key, value, expire)

    def get_list(self, key: str) -> list:
        result = self.redis_cli.get(key)
        if result is not None:
            result = pickle.loads(result)
        return result

    def key_expire(self, name: str, time: int) -> bool:
        return self.redis_cli.expire(name, time)

    def key_del(self, *names) -> int:
        return self.redis_cli.delete(*names)

    def key_rename(self, source, destination) -> bool:
        try:
            self.redis_cli.rename(source, destination)
            return True
        except redis.exceptions.ResponseError:
            return False

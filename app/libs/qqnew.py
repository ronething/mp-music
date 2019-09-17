# -*- coding: utf-8 -*-
"""
    mp-music.qqnew	
    ~~~~~~~~~~~~~~

    :copyright: (c) 2019 by ashing.
"""

from QQMusicAPI import QQMusic
from app import redis_cli


class Music(object):
    """music 对象 保存三个属性"""

    def __init__(self, title="", singer="", url=""):
        self.title = title
        self.singer = singer
        self.url = url


def qq_search(keyword):
    """根据 keyword 搜索歌曲"""
    music_list = QQMusic.search(keyword)
    if not music_list.data:
        redis_cli.set_list(key=keyword, value=[], expire=300)
        return []
    song = music_list.data[0]
    music = Music(song.title, ",".join([i.name for i in song.singer]), song.song_url())
    redis_cli.set_list(key=keyword, value=[music], expire=300)
    print("保存成功")
    return [music]


if __name__ == '__main__':
    qq_search("以后还是朋友")

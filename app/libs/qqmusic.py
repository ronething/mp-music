# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@time: 2019-04-02 01:35
@mail: axingfly@gmail.com

Less is more.
"""
import random

import requests
from music_dl.exceptions import RequestError, ResponseError
import os
import re
import datetime
import logging
import click
from music_dl.utils import colorize

config = {
    # 自定义来源 -s --source
    "source": "qq netease kugou baidu xiami",
    # 自定义数量 -c --count
    "count": 5,
    # 保存目录 -o --outdir
    "outdir": ".",
    # 搜索关键字
    "keyword": "",
    # 显示详情
    "verbose": False,
    # 搜索结果排序和去重
    "merge": False,
    # 代理
    "proxies": None,
    # 一般情况下的headers
    "fake_headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # noqa
        "Accept-Charset": "UTF-8,*;q=0.5",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "en-US,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0",  # noqa
        "referer": "https://www.google.com",
    },
    # QQ下载音乐不能没有User-Agent
    # 百度下载音乐User-Agent不能是浏览器
    # 下载时的headers
    "wget_headers": {
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "User-Agent": "Wget/1.19.5 (darwin17.5.0)",
    },
    # 移动端useragent
    "ios_useragent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46"
                     + " (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
}


def qq_search(keyword) -> list:
    """ 搜索音乐 """
    # count = config.get("count") or 5
    count = 1  # 默认第一首
    params = {"w": keyword, "format": "json", "p": 1, "n": count}
    s = requests.Session()
    s.headers.update(config.get("fake_headers"))
    if config.get("proxies"):
        s.proxies.update(config.get("proxies"))
    s.headers.update(
        {"referer": "http://m.y.qq.com", "User-Agent": config.get("ios_useragent")}
    )

    music_list = []
    r = s.get("http://c.y.qq.com/soso/fcgi-bin/search_for_qq_cp", params=params)
    if r.status_code != requests.codes.ok:
        raise RequestError(r.text)
    j = r.json()
    if j["code"] != 0:
        raise ResponseError(r.text)

    for m in j["data"]["song"]["list"]:
        # 获得歌手名字
        singers = [s["name"] for s in m["singer"]]
        music = Music()
        music.source = "qq"
        music.id = m["songid"]
        music.title = m["songname"]
        music.singer = "、".join(singers)
        music.album = m["albumname"]
        music.duration = m["interval"]
        music.size = round(m["size128"] / 1048576, 2)
        # 特有字段
        music.mid = m["songmid"]

        qq_download(music)

        music_list.append(music)

    return music_list


def qq_download(music):
    """ 根据songmid等信息获得下载链接 """
    # 计算vkey
    guid = str(random.randrange(1000000000, 10000000000))
    params = {"guid": guid, "format": "json", "json": 3}
    s = requests.Session()
    s.headers.update(config.get("fake_headers"))
    if config.get("proxies"):
        s.proxies.update(config.get("proxies"))
    s.headers.update(
        {"referer": "http://y.qq.com", "User-Agent": config.get("ios_useragent")}
    )

    r = s.get("http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg", params=params)
    if r.status_code != requests.codes.ok:
        raise RequestError(r.text)
    j = r.json()
    if j["code"] != 0:
        raise ResponseError(r.text)

    vkey = j["key"]

    for prefix in ["M800", "M500", "C400"]:
        url = "http://dl.stream.qqmusic.qq.com/%s%s.mp3?vkey=%s&guid=%s&fromtag=1" % (
            prefix,
            music.mid,
            vkey,
            guid,
        )
        music.url = url
        if music.avaiable:
            music.rate = 320 if prefix == "M800" else 128
            break

    # music.download()


class Music:
    """
        定义music对象，
        包括基本属性（如title，singer，url等）
        以及一些方法（如download，info等）
    """

    def __init__(self):
        self.idx = 0
        self.id = ""
        self.title = ""
        self.ext = "mp3"
        self.singer = ""
        self.album = ""
        self.size = ""
        self.rate = ""
        self.source = ""
        self._duration = ""
        self._url = ""
        self.outdir = config.get("outdir")
        self.verbose = config.get("verbose")
        self.logger = logging.getLogger(__name__)

    def __str__(self):
        """ 在打印详情时调用 """
        idx = colorize("[ %s ] " % self.idx, "cyan")
        source = colorize("%s" % self.source.upper(), self.source)
        return "\n ------------ \n" + _(
            " -> 来源: {idx}{source} #{id}\n"
            " -> 歌曲: {title}\n"
            " -> 歌手: {singer}\n"
            " -> 专辑: {album}\n"
            " -> 时长: {duration}\n"
            " -> 大小: {size}MB\n"
            " -> 比特率: {rate}\n"
            " -> URL: {url} \n"
        ).format(
            idx=idx,
            source=source,
            id=self.id,
            title=self.title,
            singer=self.singer,
            album=self.album,
            duration=self.duration,
            size=self.size,
            rate=self.rate,
            url=self.url,
        )

    @property
    def avaiable(self):
        """ 是否有效，如果URL为None或大小为0则无效 """
        return self.url and self.size

    @property
    def name(self):
        """ 歌曲文件名 """
        return "%s - %s.%s" % (self.singer, self.title, self.ext)

    @property
    def duration(self):
        """ 持续时间 H:M:S """
        return self._duration

    @duration.setter
    def duration(self, seconds):
        self._duration = str(datetime.timedelta(seconds=int(seconds)))

    @property
    def info(self):
        """ 歌曲摘要信息，列出搜索歌曲时使用 """
        idx = colorize(" [ %2s ] " % self.idx, "cyan")
        source = colorize("%7s" % self.source.upper(), self.source)
        size = colorize("%5sMB" % self.size, "yellow")
        title = colorize(self.title, "yellow")
        v = colorize(" | ", self.source)
        h = colorize(" - ", self.source)
        return (
                idx
                + source
                + v
                + self.duration
                + h
                + size
                + h
                + self.singer
                + h
                + title
                + h
                + self.album
        )

    @property
    def row(self):
        """ 歌曲摘要信息，列出搜索歌曲时使用PrettyTable """
        keywords = re.split(";|,|\s|\*", config.get("keyword"))

        def highlight(s, k):
            return s.replace(k, colorize(k, "xiami")).replace(
                k.title(), colorize(k.title(), "xiami")
            )

        ht_singer = self.singer if len(self.singer) < 30 else self.singer[:30] + "..."
        ht_title = self.title if len(self.title) < 30 else self.title[:30] + "..."
        ht_album = self.album if len(self.album) < 20 else self.album[:20] + "..."
        for k in keywords:
            if not k:
                continue
            ht_singer = highlight(ht_singer, k)
            ht_title = highlight(ht_title, k)
            ht_album = highlight(ht_album, k)

        size = "%sMB" % self.size
        ht_size = size if int(self.size) < 8 else colorize(size, "flac")

        return [
            colorize(self.idx, "baidu"),
            ht_singer,
            ht_title,
            ht_size,
            self.duration,
            ht_album,
            self.source.upper(),
        ]

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        """ 设置URL的时候同时更新size大小 """
        try:
            r = requests.get(
                url,
                stream=True,
                headers=config.get("wget_headers"),
                proxies=config.get("proxies"),
            )
            self._url = url
            size = int(r.headers.get("Content-Length", 0))
            # 转换成MB并保留两位小数
            self.size = round(size / 1048576, 2)
        except Exception as e:
            self.logger.info(_("请求失败: {url}").format(url=url))
            self.logger.info(e)

    @property
    def fullname(self):
        """ 唯一有效的完整路径，如果冲突则在名称加数字，如music（1）.mp3 """
        outfile = os.path.abspath(os.path.join(self.outdir, self.name))
        if os.path.exists(outfile):
            name, ext = self.name.rsplit(".", 1)
            names = [x for x in os.listdir(self.outdir) if x.startswith(name)]
            names = [x.rsplit(".", 1)[0] for x in names]
            suffixes = [x.replace(name, "") for x in names]
            # filter suffixes that match ' (x)' pattern
            suffixes = [
                x[2:-1] for x in suffixes if x.startswith(" (") and x.endswith(")")
            ]
            indexes = [int(x) for x in suffixes if set(x) <= set("0123456789")]
            idx = 1
            if indexes:
                idx += sorted(indexes)[-1]
            outfile = os.path.abspath(
                os.path.join(self.outdir, "%s (%d).%s" % (name, idx, ext))
            )
        return outfile

    def download(self):
        """ 下载音乐 """
        if config.get("verbose"):
            click.echo(str(self))
        else:
            click.echo(self.info)

        outfile = self.fullname
        try:
            r = requests.get(
                self.url,
                stream=True,
                headers=config.get("wget_headers"),
                proxies=config.get("proxies"),
            )
            total_size = int(r.headers["content-length"])
            with click.progressbar(length=total_size, label=_("下载中...")) as bar:
                with open(outfile, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
            click.echo(_("已保存到: {outfile}").format(outfile=outfile) + "\n")
        except Exception as e:
            click.echo("")
            self.logger.error(_("下载音乐失败: ") + "\n")
            self.logger.error(_("URL: {url}").format(url=self.url) + "\n")
            self.logger.error(_("位置: {outfile}").format(outfile=outfile) + "\n")
            if self.verbose:
                self.logger.error(e)


if __name__ == '__main__':
    a = qq_search(keyword='?')
    for i in a:
        print(i.title, i.singer, i.url)

# -*- coding:utf-8 _*-
""" 
@author: ronething 
@time: 2019-04-02 00:54 
@mail: axingfly@gmail.com

Less is more.
"""
import hashlib
import threading
from time import time

from flask import request, current_app, make_response, render_template

from app.libs.qqnew import qq_search
from app.libs.utils import get_mes
from app.web import web
from app import redis_cli


@web.route('/flask', methods=["GET", "POST"])
def mp():
    if request.method == "GET":
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        mp_list = [current_app.config["TOKEN"], timestamp, nonce]
        mp_list.sort()
        mp_signature = "".join(mp_list)
        hashmp_signature = hashlib.sha1(
            mp_signature.encode('utf-8')).hexdigest()
        if hashmp_signature == signature:
            return echostr
        else:
            print('token error')
            return 'error'

    if request.method == "POST":
        res = get_mes(request.data)
        # print(res)
        if res['type'] == 'other':
            # 如果不是 text 类型返回失败
            send_mes = make_response(render_template('send/text.xml', to_user=res['from_user'],
                                                     from_user=res['to_user'], create_time=int(
                                                         time()),
                                                     content='请输入文本😁'))
            send_mes.headers['Content-Type'] = 'text/xml'
            return send_mes
        else:
            # redis 缓存
            kw = res['content']
            print("kw is {}".format(kw))
            music = redis_cli.get_list(kw)
            if not music and isinstance(music, list):
                # qq_search res is []
                send_mes = make_response(render_template('send/text.xml', to_user=res['from_user'],
                                                         from_user=res['to_user'], create_time=int(
                                                             time()),
                                                         content='没有找到音乐🎸'))
                send_mes.headers['Content-Type'] = 'text/xml'
                return send_mes

            if not music:
                # None 另启线程
                cache_thread = threading.Thread(target=qq_search, args=(kw,))
                cache_thread.start()
                send_mes = make_response(render_template('send/text.xml', to_user=res['from_user'],
                                                         from_user=res['to_user'], create_time=int(
                                                             time()),
                                                         content='搜索结果已经加入缓存，请再次输入'))
                send_mes.headers['Content-Type'] = 'text/xml'
                return send_mes

            else:
                music = music[0]

            # TODO music url 可能是 m4a 问题 无法直接点击播放按钮播放
            music_url = (music.url).replace("http", "https")
            print(music_url)
            # 回复音乐消息
            send_mes = make_response(render_template('send/music.xml', to_user=res['from_user'],
                                                     from_user=res['to_user'], create_time=int(
                                                         time()),
                                                     title=music.title, desc=music.singer,
                                                     music_url=music_url))
            send_mes.headers['Content-Type'] = 'text/xml'
            return send_mes

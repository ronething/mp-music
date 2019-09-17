# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@time: 2019-04-02 00:46 
@mail: axingfly@gmail.com

Less is more.
"""


from flask import Flask 
from app.libs.utils import get_redis_config
from app.libs.conn_redis import ConnRedis

redis_cli = ConnRedis(config=get_redis_config())

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.secure")
    app.config.from_object("app.config.setting")
    register_blueprint(app)

    return app


def register_blueprint(app):
    from app.web import web
    app.register_blueprint(web)

# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@time: 2019-04-02 00:49 
@mail: axingfly@gmail.com

Less is more.
"""

import os
from dotenv import load_dotenv
load_dotenv()

environ = os.getenv('FLASK_ENV', 'development')

PORT = 7000

if environ == 'production':

    DEBUG = False

    HOST = '0.0.0.0'

else:

    DEBUG = True

    HOST = '127.0.0.1'

# 添加 TOKEN
# TOKEN = 'xxxx'

# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@time: 2019-04-02 00:46 
@mail: axingfly@gmail.com

Less is more.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])

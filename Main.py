"""
This file is the main file, which has imported userlogin and postclass.
"""

import requests
from UserLogin import userlogin
from PostClass import postclass


http_main = requests.session()
# 用户登录
http_main = userlogin(http_main)
# 自由选课
postclass(http_main)

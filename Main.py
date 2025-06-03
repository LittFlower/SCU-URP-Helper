"""
This file is the main file, which has imported userlogin and postclass.
"""

import requests
from UserLogin import userlogin
from PostClass import postclass
from teacherEvaluate import teacherEvaluate
from sys import argv

print("[*]Hint: If you want to start the feature to automaticly evaluate teachers, \
    you should pass in the parameter E.")

http_main = requests.session()
# 用户登录
http_main = userlogin(http_main)


if argv[0] == 'E':
    # TODO: teacherEvaluate
    teacherEvaluate(http_main)
    exit()

# 自由选课
postclass(http_main)

"""
This file is the main file, which has imported userlogin and postclass.
"""

import requests
import staticINF
from UserLogin import userlogin
from GetMajorid import fetch_major_id
from PostClass import postclass
from teacherEvaluate import teacherEvaluate
import sys

# staticINF.print_log("Hint: If you want to start the feature to automaticly evaluate teachers, you should pass in the parameter E.", "INFO")

staticINF.print_log("来 https://github.com/LittFlower/SCU-URP-Helper 点点 star 谢谢喵", "INFO")

if not staticINF.MajorId:
    fetched_major = fetch_major_id(auto_save=True)
    if not fetched_major:
        staticINF.print_log("未能获取专业号，程序退出。", "ERROR")
        exit(-1)

http_main = requests.session()
http_main = userlogin(http_main)


if argv[0] == 'E':
    # TODO: teacherEvaluate
    teacherEvaluate(http_main)
    exit()


postclass(http_main)

from UserLogin import userlogin
from PostClass import postclass
import requests


http_main = requests.session()
# 用户登录
http_main = userlogin(http_main)
# 自由选课
postclass(http_main)

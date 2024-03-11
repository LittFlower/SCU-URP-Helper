from staticINF import *

import requests
# from PIL import Image
import hashlib


def userlogin(_http_main: requests.session) -> requests.session:
    """ userlogin
    this func can log in the user account and keep it to future.
    :param _http_main: the main http session.
    :return: a requests session which has been updated.
    """

    res = _http_main.get(login_url, headers=http_head)
    if res.status_code != 200:
        print_log("Login Error!")

    token_pos = res.text.find("tokenValue")
    token = res.text[token_pos + 37: token_pos + 69]
    print_log(token)

    # username = UserName
    password = hashlib.md5(PassWord.encode()).hexdigest()

    code_photo = _http_main.get(captcha_url, headers=http_head)
    with open("code.jpg", "wb") as photo:
        photo.write(code_photo.content)
        photo.close()

    code = input("输入图片验证码：")
    login_data["tokenValue"] = token
    login_data["j_password"] = password
    login_data["j_captcha"] = code

    res = _http_main.post(security_check_url, login_data, http_head)

    if res.text.find('验证码错误') != -1:
        print_log("[登录未成功]：验证码错误")
    elif res.text.find('token校验失败') != -1:
        print_log("[登录未成功]: token校验失败")
    elif res.text.find('退出系统') == -1:
        print_log("[登录未成功]：账号密码错误")
    if res.text.find('退出系统') != -1:
        print_log("[已成功登录]：成功登录系统")
        return _http_main

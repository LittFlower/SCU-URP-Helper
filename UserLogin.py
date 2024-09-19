from staticINF import *

import requests
# from PIL import Image
import hashlib
import ddddocr

# def read_pwd()


def userlogin(_http_main: requests.session) -> requests.session:
    """ userlogin
    this func can log in the user account and keep it to future.
    :param _http_main: the main http session.
    :return: a requests session which has been updated.
    """
    ocr: ddddocr.DdddOcr = ddddocr.DdddOcr()
    # usernameread_pwd()

    login_attempts = 0  # 追踪登录尝试次数
    while login_attempts < 100:
        res = _http_main.get(login_url, headers=http_head)
        if res.status_code != 200:
            print_log("Login Error!")

        token_pos = res.text.find("tokenValue")
        token = res.text[token_pos + 37: token_pos + 69]
        print_log(token)

        magicStr = "{Urp602019}"
        # username = UserName
        # update: jwc has updated the logic of login.
        # password = hashlib.md5(PassWord.encode()).hexdigest()
        password = hashlib.md5((PassWord + magicStr).encode()).hexdigest() + '*' + \
            hashlib.md5(PassWord.encode()).hexdigest()

        code_photo = _http_main.get(captcha_url, headers=http_head)
        with open("code.jpg", "wb") as photo:
            photo.write(code_photo.content)
            photo.close()
        image = code_photo.content
        code = ocr.classification(image)
        # code = input("输入图片验证码：")
        login_data["tokenValue"] = token
        login_data["j_password"] = password
        login_data["j_captcha"] = code

        res = _http_main.post(security_check_url, login_data, http_head)

        if res.text.find('验证码错误') != -1:
            print_log("[登录未成功]：验证码不正确，自动进行下一次尝试")
            login_attempts += 1  # 增加尝试次数
            continue  # 继续下一次尝试
        elif res.text.find('token校验失败') != -1:
            print_log("[登录未成功]: token校验失败")
            exit(-1)  # token校验失败时，退出循环
        elif res.text.find('退出系统') == -1:
            print_log("[登录未成功]：账号密码错误")
            exit(-1)  # 账号密码错误时，退出循环
        if res.text.find('退出系统') != -1:
            print_log("[已成功登录]：成功登录系统")
            return _http_main  # 登录成功，返回会话

    return _http_main  # 超过尝试次数或其他原因退出循环时，返回会话

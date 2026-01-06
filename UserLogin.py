from staticINF import *
import requests
import hashlib
import ddddocr


def encrypt(content: str) -> str:
    """
    Double-MD5 the given plaintext password and return the combined hash.
    :param content: plaintext password.
    :return: concatenated hash string used by URP.
    """
    magicStr = "{Urp602019}"
    res1 = hashlib.md5((content + magicStr).encode()).hexdigest()
    res1 = hashlib.md5(res1.encode()).hexdigest()
    res2 = hashlib.md5(content.encode()).hexdigest()
    res2 = hashlib.md5(res2.encode()).hexdigest()
    return res1 + "*" + res2


def userlogin(_http_main: requests.session) -> requests.session:
    """
    Log in with the configured credentials, solving captcha via ddddocr, and return an authenticated session.
    Retries on captcha errors, exits on token or credential errors.
    :param _http_main: existing requests session to use.
    :return: authenticated session.
    """
    ocr: ddddocr.DdddOcr = ddddocr.DdddOcr()

    login_attempts = 0  # 追踪登录尝试次数
    while login_attempts < 100:
        res = _http_main.get(login_url, headers=http_head)
        if res.status_code != 200:
            print_log("Login Error!")

        token_pos = res.text.find("tokenValue")
        token = res.text[token_pos + 37: token_pos + 69]
        print_log(token)

        # update: jwc has updated the logic of login.
        password = encrypt(PassWord)
        code_photo = _http_main.get(captcha_url, headers=http_head)
        with open("code.jpg", "wb") as photo:
            photo.write(code_photo.content)
            photo.close()
        image = code_photo.content
        code = ocr.classification(image)
        local_login = login_data.copy()
        local_login["j_username"] = UserName
        local_login["tokenValue"] = token
        local_login["j_password"] = password
        local_login["j_captcha"] = code

        res = _http_main.post(security_check_url,
                              data=local_login,
                              headers=http_head)

        if res.text.find('验证码错误') != -1:
            print_log("[登录未成功]：验证码不正确，自动进行下一次尝试")
            login_attempts += 1
            continue
        elif res.text.find('token校验失败') != -1:
            print_log("[登录未成功]: token校验失败")
            exit(-1)
        # update: jwc has updated the ui.
        elif res.text.find('用户名或密码错误!') == -1:
            # print_log(res.text)
            print_log("[已成功登录]：成功登录系统")
            return _http_main
        else:
            print_log("[登录未成功]：账号密码错误")
            exit(-1)

    return _http_main  # 超过尝试次数或其他原因退出循环时，返回会话

# from UserLogin import userlogin
from staticINF import *
import ddddocr
import requests
import json
import time


def sanitize_text(value: str) -> str:
    if not isinstance(value, str):
        return value
    cleaned = value.encode("utf-8", "ignore").decode("utf-8", "ignore")
    if cleaned != value:
        print_log("输入包含不可编码字符，已自动清理。")
    return cleaned


def show_class(class_loop: dict, cnt: int) -> None:
    """ Show the class
    :param class_loop: a class.
    :param cnt: index of class.
    :return: None
    """
    class_name = class_loop['kcm']
    class_id = class_loop['kch']
    class_free = class_loop['bkskyl']
    class_tech = class_loop['skjs']
    class_kxh = class_loop['kxh']
    print(f"{cnt}. {class_id}_{class_kxh} {class_name} {class_tech} {class_free}")


def verify(visit: dict) -> bool:
    """ Verify
    :param visit: a visit dictionary of class list.
    :return: Bool.
    """

    for i in visit.values():
        if not i:
            return True
    return False


def equal_class(choice: dict, class_loop: dict) -> bool:
    """ Equal class
    This func can judge whether the class A equal to the class B.
    :param choice: the first class
    :param class_loop: the second class
    :return: Bool
    """
    # show_class(choice, 1)
    if choice['kcm'] == class_loop['kcm'] and \
            choice['kch'] == class_loop['kch'] and \
            choice['kxh'] == class_loop['kxh'] and \
            choice['jasm'] == class_loop['jasm']:
        return True
    else:
        return False


def get_class_list(_http_main: requests.session, kcm: str) -> list:
    """get class list
    This func can get a list of classes by searching a key word.
    :param _http_main: the http main.
    :param kcm: the key word.
    :return: a list of class.
    """
    class_list: list = []
    clean_kcm = sanitize_text(kcm)
    if not clean_kcm.strip():
        print_log("课程关键词为空，跳过。")
        return []
    local_query = query_class_data.copy()
    local_query['kcm'] = clean_kcm
    res = _http_main.get(courseSelect_url, headers=http_head)

    if res.status_code != 200 or res.text.find("自由选课") == -1:
        print_log("自由选课失败! Net Error!")
        return []
    else:
        print_log("[成功获取课表]：成功进入课表页面，正在读取教务处课表列表，请耐心等待")
        res_post: requests.Response = \
            _http_main.post(free_course_select_url,
                            data=local_query,
                            headers=http_head)

    if res_post.status_code != 200:
        print_log(f"获取课程列表失败，状态码: {res_post.status_code}")
        return []

    raw_text = res_post.text or ""
    if not raw_text.strip():
        print_log("课程列表响应为空，可能网络异常或登录过期。")
        return []

    try:
        res_json = json.loads(raw_text)
    except json.JSONDecodeError:
        snippet = raw_text.strip()[:200]
        print_log("课程列表响应不是 JSON，可能登录过期或被重定向。")
        print_log(f"响应片段: {snippet}")
        return []

    if not isinstance(res_json, dict):
        print_log("课程列表响应格式异常，无法解析。")
        return []

    if "rwRxkZlList" not in res_json:
        print_log("课程列表响应缺少 rwRxkZlList 字段。")
        return []

    if type(res_json['rwRxkZlList']) is str:
        try:
            class_list = json.loads(res_json['rwRxkZlList'])
        except json.JSONDecodeError:
            print_log("课程列表字段解析失败。")
            return []
    elif type(res_json['rwRxkZlList']) is list:
        class_list = res_json['rwRxkZlList']
    else:
        print_log("res_tabs to list error!")
        return []

    return class_list


def add_class(_http_main: requests.session) -> list:
    choice_class: list = []
    while True:
        class_name = sanitize_text(
            input("请输入一个课程名（关键词）或输入 'done' 完成选课：")
        )
        if class_name.strip().lower() == 'done':
            break
        if not class_name.strip():
            print_log("课程关键词为空，跳过。")
            continue

        class_list = get_class_list(_http_main, class_name)

        # 展示相关课程
        class_count = 0
        for class_loop in class_list:
            class_count += 1
            show_class(class_loop, class_count)

        if class_count == 0:
            print_log("没有搜到相关课程。")
            continue

        # 选择相关课程
        choice_input = input("[请输入编号, 中间以英文逗号隔开]：").split(",")
        for choice in choice_input:
            if choice.isdigit() and int(choice) in range(1, class_count + 1):
                choice_class.append(class_list[int(choice) - 1])

    return choice_class


def postclass(_http_main: requests.session) -> None:
    # 自由选课
    ocr: ddddocr.DdddOcr = ddddocr.DdddOcr()
    visit: dict = {}

    choice_class = add_class(_http_main)
    if len(choice_class) == 0:
        print_log("戳啦！需要先添加课程哦～")

    for choice in choice_class:
        temp = choice['kch'] + "_" + choice['kxh'] + "_" + choice['zxjxjhh']
        visit[temp] = False

    while verify(visit):
        try:
            data = _http_main.get(courseSelect_url, headers=http_head)
            # TODO: 写个重新登陆
            time.sleep(SleepTime)
        except requests.exceptions.ConnectionError:
            print_log("网络错误")
            continue

        try:
            for choice in choice_class:  # 遍历选课队列
                class_list = get_class_list(_http_main, choice['kcm'])  # 获取相关课程列表

                for class_loop in class_list:
                    if equal_class(class_loop, choice):
                        current_free = class_loop['bkskyl']  # 获取当前课余量
                        print(f"当前课程: {class_loop['kcm']}, 课余量: {current_free}")

                        if current_free > 0:
                            class_name_kxh = ""
                            class_name = f"{choice['kcm']}_{choice['kxh']}"
                            for i in range(0, len(class_name)):
                                class_name_kxh += \
                                    str(int(hex(ord(class_name[i])).zfill(4), 16)) + ","
                            # 获得 token
                            temp = data.text.find('id=\"tokenValue\"')
                            token = data.text[temp + 23: temp + 55]
                            # 获得验证码
                            image: requests.Response.content = \
                                _http_main.get(yzmPic_url, headers=http_head).content
                            with open("verify.jpg", "wb") as photo:
                                photo.write(image)
                                photo.close()
                            code = ocr.classification(image)
                            # 配置 post
                            local_post = post_class_data.copy()
                            local_post["kcIds"] = \
                                choice['kch'] + "_" + choice['kxh'] + "_" + choice['zxjxjhh']
                            local_post["kcms"] = class_name_kxh
                            local_post["tokenValue"] = token
                            local_post["inputCode"] = code[-4:]
                            print_log("自动识别验证码：" + code[-4:])
                            # print_log(post_class_data["kcms"])
                            # print_log(choice['kxh'])
                            print_log(local_post)

                            try:
                                data = _http_main.post(courseSubmit_url,
                                                       data=local_post,
                                                       headers=http_head)
                                # print_log(post_class_data)
                            except requests.exceptions.ConnectionError:
                                print_log("网络错误")
                                continue

                            if data.text.find("ok") != -1:
                                # print(post_class_data)
                                print_log(data.text)
                                visit[local_post["kcIds"]] = True
                                break
                            elif data.text.find("错误") != -1:
                                print_log("自动识别验证码失败，正在重新尝试")
                                break
                            else:
                                print_log("错啦～")
                        else:
                            print_log("课余量不足，跳过此课程")
        except requests.exceptions.ConnectionError:
            print_log("网络错误！")

    return

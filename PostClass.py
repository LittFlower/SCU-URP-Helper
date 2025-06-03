# from UserLogin import userlogin
from staticINF import *
import ddddocr
import requests
import json
import time


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
    query_class_data['kcm'] = kcm
    res = _http_main.get(courseSelect_url, headers=http_head)

    if res.status_code != 200 or res.text.find("自由选课") == -1:
        print_log("自由选课失败! Net Error!")
        return []
    else:
        print_log("[成功获取课表]：成功进入课表页面，正在读取教务处课表列表，请耐心等待")
        res_post: requests.Response = \
            _http_main.post(free_course_select_url, query_class_data, http_head)

    res_json = json.loads(res_post.text)

    if type(res_json['rwRxkZlList']) is str:
        class_list = json.loads(res_json['rwRxkZlList'])
    elif type(res_json['rwRxkZlList']) is list:
        class_list = res_json['rwRxkZlList']
    else:
        print_log("res_tabs to list error!")

    return class_list


def add_class(_http_main: requests.session) -> list:
    choice_class: list = []
    while True:
        class_name = input("请输入一个课程名（关键词）或输入 'done' 完成选课：")
        if class_name.lower() == 'done':
            break

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
                            choice['kcm'] += "_" + choice['kxh']
                            for i in range(0, len(choice['kcm'])):
                                class_name_kxh += \
                                    str(int(hex(ord(choice['kcm'][i])).zfill(4), 16)) + ","
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
                            post_class_data["kcIds"] = \
                                choice['kch'] + "_" + choice['kxh'] + "_" + choice['zxjxjhh']
                            post_class_data["kcms"] = class_name_kxh
                            post_class_data["tokenValue"] = token
                            post_class_data["inputCode"] = code[-4:]
                            print_log("自动识别验证码：" + code[-4:])
                            # print_log(post_class_data["kcms"])
                            # print_log(choice['kxh'])
                            print_log(post_class_data)

                            try:
                                data = _http_main.post(courseSubmit_url,
                                                       post_class_data, http_head)
                                # print_log(post_class_data)
                            except requests.exceptions.ConnectionError:
                                print_log("网络错误")
                                continue

                            if data.text.find("ok") != -1:
                                # print(post_class_data)
                                print_log(data.text)
                                visit[post_class_data["kcIds"]] = True
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

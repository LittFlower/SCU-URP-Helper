# from UserLogin import userlogin
from staticINF import *
import ddddocr
import requests
import json
import time
import os
import sys
import traceback
from redmail import EmailSender
from smtplib import SMTP_SSL


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
    # 处理搜索关键词，移除或替换无法编码的字符
    kcm = kcm.encode('utf-8', errors='ignore').decode('utf-8')
    query_class_data['kcm'] = kcm
    res = _http_main.get(courseSelect_url, headers=http_head)

    if res.status_code != 200 or res.text.find("自由选课") == -1:
        print_log("自由选课失败! Net Error!")
        return []
    else:
        print_log("[成功获取课表]：成功进入课表页面，正在读取教务处课表列表，请耐心等待")
        try:
            res_post: requests.Response = \
                _http_main.post(free_course_select_url, query_class_data, http_head)
        except UnicodeEncodeError as e:
            print_log(f"编码错误：{str(e)}")
            # 尝试使用不同的编码方式
            query_class_data['kcm'] = kcm.encode('ascii', errors='ignore').decode('ascii')
            res_post: requests.Response = \
                _http_main.post(free_course_select_url, query_class_data, http_head)

    try:
        res_json = json.loads(res_post.text)

        if type(res_json['rwRxkZlList']) is str:
            class_list = json.loads(res_json['rwRxkZlList'])
        elif type(res_json['rwRxkZlList']) is list:
            class_list = res_json['rwRxkZlList']
        else:
            print_log("res_tabs to list error!")
    except json.JSONDecodeError as e:
        print_log(f"JSON解析错误：{str(e)}")
        print_log(f"响应内容：{res_post.text[:200]}...")  # 只打印前200个字符
        return []

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


def send_initial_email(choice_class: list) -> None:
    """Send initial email to confirm script is running and show course queue
    :param choice_class: List of courses to be selected
    :return: None
    """
    if os.environ.get("SEND_MAIL", "False").lower() != "true":
        return

    try:
        # 从环境变量读取邮箱配置
        smtp_user = os.environ["SMTP_USER"]
        smtp_pass = os.environ["SMTP_PASSWORD"]
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = int(os.environ["SMTP_PORT"])
        receive_mail = os.environ["SMTP_USER"]  # 默认发送到同一个邮箱

        email = EmailSender(
            host=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            cls_smtp=SMTP_SSL,
            use_starttls=False
        )

        # 构建课程列表文本
        course_list_text = "抢课队列中的课程：\n\n"
        for i, course in enumerate(choice_class, 1):
            course_list_text += f"{i}. {course['kcm']} ({course['kch']}_{course['kxh']})\n"
            course_list_text += f"   教师：{course['skjs']}\n"
            course_list_text += f"   课余量：{course['bkskyl']}\n\n"

        # 发送初始邮件
        email.send(
            subject="抢课脚本已启动",
            sender=smtp_user,
            receivers=[receive_mail],
            text=f"抢课脚本已成功启动并开始运行。\n\n{course_list_text}\n\n脚本将持续监控这些课程的课余量，当有余量时会自动选课并发送通知。"
        )
        print_log("✅ 初始通知邮件已发送！")
    except Exception as e:
        print_log(f"发送初始邮件失败：{str(e)}")


def send_error_email(error_msg: str, error_traceback: str) -> None:
    """Send error notification email when script encounters an error
    :param error_msg: Error message
    :param error_traceback: Full error traceback
    :return: None
    """
    if os.environ.get("SEND_MAIL", "False").lower() != "true":
        return

    try:
        # 从环境变量读取邮箱配置
        smtp_user = os.environ["SMTP_USER"]
        smtp_pass = os.environ["SMTP_PASSWORD"]
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = int(os.environ["SMTP_PORT"])
        receive_mail = os.environ["SMTP_USER"]  # 默认发送到同一个邮箱

        email = EmailSender(
            host=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            cls_smtp=SMTP_SSL,
            use_starttls=False
        )

        # 发送错误通知邮件
        email.send(
            subject="抢课脚本异常退出通知",
            sender=smtp_user,
            receivers=[receive_mail],
            text=f"抢课脚本遇到错误并退出：\n\n错误信息：\n{error_msg}\n\n详细错误信息：\n{error_traceback}"
        )
        print_log("✅ 错误通知邮件已发送！")
    except Exception as e:
        print_log(f"发送错误通知邮件失败：{str(e)}")


def send_exit_email() -> None:
    """Send exit notification email when script exits normally
    :return: None
    """
    if os.environ.get("SEND_MAIL", "False").lower() != "true":
        return

    try:
        # 从环境变量读取邮箱配置
        smtp_user = os.environ["SMTP_USER"]
        smtp_pass = os.environ["SMTP_PASSWORD"]
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = int(os.environ["SMTP_PORT"])
        receive_mail = os.environ["SMTP_USER"]  # 默认发送到同一个邮箱

        email = EmailSender(
            host=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            cls_smtp=SMTP_SSL,
            use_starttls=False
        )

        # 发送退出通知邮件
        email.send(
            subject="抢课脚本正常退出通知",
            sender=smtp_user,
            receivers=[receive_mail],
            text="抢课脚本已正常退出。\n\n如果这是意外退出，请检查日志并重新运行脚本。"
        )
        print_log("✅ 退出通知邮件已发送！")
    except Exception as e:
        print_log(f"发送退出通知邮件失败：{str(e)}")


def postclass(_http_main: requests.session) -> None:
    try:
        # 自由选课
        ocr: ddddocr.DdddOcr = ddddocr.DdddOcr()
        visit: dict = {}

        choice_class = add_class(_http_main)
        if len(choice_class) == 0:
            print_log("戳啦！需要先添加课程哦～")
            return

        # 发送初始邮件
        send_initial_email(choice_class)

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
                    class_list = get_class_list(_http_main, choice['kcm'])

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
                                print_log(post_class_data)

                                try:
                                    data = _http_main.post(courseSubmit_url,
                                                           post_class_data, http_head)
                                except requests.exceptions.ConnectionError:
                                    print_log("网络错误")
                                    continue

                                if data.text.find("ok") != -1:
                                    print_log(data.text)
                                    visit[post_class_data["kcIds"]] = True
                                    # 发送抢课成功通知邮件
                                    send_notification_email(
                                        course_name=class_loop['kcm'],
                                        course_id=class_loop['kch'],
                                        course_kxh=class_loop['kxh']
                                    )
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
            except json.JSONDecodeError as e:
                error_msg = f"JSON解析错误：{str(e)}"
                print_log(error_msg)
                send_error_email(error_msg, traceback.format_exc())
                raise
            except Exception as e:
                error_msg = f"发生未知错误：{str(e)}"
                print_log(error_msg)
                send_error_email(error_msg, traceback.format_exc())
                raise

    except Exception as e:
        error_msg = f"发生错误：{str(e)}"
        print_log(error_msg)
        send_error_email(error_msg, traceback.format_exc())
        raise
    finally:
        send_exit_email()


def send_notification_email(course_name: str, course_id: str, course_kxh: str) -> None:
    """Send notification email when successfully selected a course
    :param course_name: Name of the course
    :param course_id: ID of the course
    :param course_kxh: Class number of the course
    :return: None
    """
    if os.environ.get("SEND_MAIL", "False").lower() != "true":
        return

    try:
        # 从环境变量读取邮箱配置
        smtp_user = os.environ["SMTP_USER"]
        smtp_pass = os.environ["SMTP_PASSWORD"]
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = int(os.environ["SMTP_PORT"])
        receive_mail = os.environ["SMTP_USER"]  # 默认发送到同一个邮箱

        email = EmailSender(
            host=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            cls_smtp=SMTP_SSL,
            use_starttls=False
        )

        # 发送通知邮件
        email.send(
            subject=f"抢课成功通知 - {course_name}",
            sender=smtp_user,
            receivers=[receive_mail],
            text=f"恭喜！您已成功抢到以下课程：\n\n课程名称：{course_name}\n课程编号：{course_id}\n课序号：{course_kxh}\n\n请及时登录教务系统确认选课结果。"
        )
        print_log("✅ 抢课成功通知邮件已发送！")
    except Exception as e:
        print_log(f"发送邮件失败：{str(e)}")

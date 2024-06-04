"""
这个文件里存放了一些会用到的 const.
"""

login_url = "http://zhjw.scu.edu.cn/login"
security_check_url = "http://zhjw.scu.edu.cn/j_spring_security_check"
captcha_url = "http://zhjw.scu.edu.cn/img/captcha.jpg"
courseSelect_url = "http://zhjw.scu.edu.cn/student/courseSelect/courseSelect/index"
free_course_select_url = "http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/courseList"
courseSubmit_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/checkInputCodeAndSubmit"
yzmPic_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/getYzmPic.jpg"

# 请初始化！
UserName = "" #账号
PassWord = "" #密码
MajorId = "202403190401" #专业号 例如网安是10185
SleepTime = 1 #查找课程的间隔，单位是秒

login_data = {
    "tokenValue": "",
    "j_username": UserName,
    "j_password": "",
    "j_captcha": ""
}

query_class_data = {
    "kkxsh": "",  # 学院号，默认为全部（空）
    # "fajhh": "10574", # 培养方案的方案号，化学(大类)：10574
    # "jhxn": "2023-2024-2-1", # 计划学年
    # "kcsxdm": "", # 课程属性：必修(001) 选修(002) 任选(003) 辅修(004)
    "kch": "",  # 课程号
    "kcm": "",  # 课程名
    "skjs": "",  # 上课教师
    "kclbdm": "",  # 课程类别
    # "xqh": "", # 真正会改变的校区 望江(01) 华西(02) 江安(03)
    "xq": "0",  # 校区
    "jc": "0"
}

post_class_data = {
    "dealType": 5,
    "kcIds": "",  # "课程号@课序号@计划学年"
    "kcms": "",  # 对课程名进行编码
    "fajhh": MajorId,  # 方案 id
    "sj": "0_0",
    "kkxsh": "",
    "kclbdm": "",
    "inputCode": "",
    "tokenValue": ""
}

http_head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 "
                  "Safari/537.36 Edg/105.0.1343.33"
}


# TODO: 日志系统
def print_log(message: str) -> None:
    print(message)

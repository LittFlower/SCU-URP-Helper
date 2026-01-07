"""
这个文件里存放了一些会用到的 const.
账号/密码/专业号/时间从 config.json 读取。
"""

import json
import os
import random
from datetime import datetime

login_url = "http://zhjw.scu.edu.cn/login"
security_check_url = "http://zhjw.scu.edu.cn/j_spring_security_check"
captcha_url = "http://zhjw.scu.edu.cn/img/captcha.jpg"
courseSelect_url = "http://zhjw.scu.edu.cn/student/courseSelect/courseSelect/index"
free_course_select_url = "http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/courseList"
courseSubmit_url = \
    "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/checkInputCodeAndSubmit"
yzmPic_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/getYzmPic.jpg"
teacherEvaluate_url = "http://zhjw.scu.edu.cn/student/teachingEvaluation/newEvaluation/"
evaluationTable_url = "http://zhjw.scu.edu.cn/student/teachingAssessment/evaluation/queryAll"

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# TODO: 日志系统
def print_log(message: str, level: str = "INFO") -> None:
    """
    Print a formatted log line with timestamp, level marker, and message.
    Supported levels: SUCCESS / INFO / DEBUG / ERROR; others fall back to INFO.
    Markers: [+] success, [*] info, [!] error, [DEBUG] debug.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lvl = (level or "INFO").upper()
    if lvl not in {"SUCCESS", "INFO", "DEBUG", "ERROR"}:
        lvl = "INFO"
    prefix = {
        "SUCCESS": "[+]",
        "INFO": "[*]",
        "ERROR": "[!]",
        "DEBUG": "[DEBUG]"
    }.get(lvl, "[*]")
    print(f"[{ts}]{prefix} {message}")


def _load_config(path: str) -> dict:
    """
    Load JSON config from the given path and return it as a dictionary.
    Raises FileNotFoundError with a helpful hint when the file is missing.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"配置文件不存在: {path}. 请复制 config.json.example 为 config.json 并填写。"
        )
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


_config = _load_config(CONFIG_PATH)

# 请在 config.json 中初始化！
UserName = _config.get("username", "")  # 账号
PassWord = _config.get("password", "")  # 密码
MajorId = str(_config.get("major_id", ""))  # 专业号 例如网安是10185 降转网安是202403190401 化学大类是10574 计算机大类是10646 化学拔尖是10587
# 现在 MajorId 可以自动获取了～
SleepTime = _config.get("sleep_time", 2)  # 查找课程间隔（秒）
SleepJitter = _config.get("sleep_jitter", 0.5)  # 查找间隔时间抖动（秒，正负浮动）

def get_sleep_interval() -> float:
    """
    Return a jittered sleep interval to simulate real browser refresh timing.
    Uses base SleepTime plus a uniform jitter in [-SleepJitter, SleepJitter],
    clamped to a minimum of 0.1 seconds.
    """
    base = float(SleepTime) if SleepTime is not None else 0.0
    jitter = float(SleepJitter) if SleepJitter is not None else 0.0
    delay = base + random.uniform(-abs(jitter), abs(jitter))
    delay = max(0.1, delay)
    # print_log(f"本次休眠 {delay:.2f}s (基础 {base}s ± 抖动 {abs(jitter)}s)", "DEBUG")
    return delay



def _persist_config(data: dict) -> None:
    """
    Persist the provided configuration dictionary back to CONFIG_PATH as JSON.
    """
    with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def set_major_id(new_major_id: str) -> str:
    """
    Update and persist the major_id in config.json and sync it into post_class_data at runtime.
    """
    global MajorId, _config
    str_id = str(new_major_id or "")
    _config["major_id"] = str_id
    _persist_config(_config)
    MajorId = str_id
    try:
        post_class_data["fajhh"] = str_id
    except Exception:
        pass
    return MajorId


login_data = {
    "lang": "zh",
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
    "kcIds": "",  # "课程号_课序号_计划学年"
    "kcms": "",  # 对课程名进行编码
    "fajhh": MajorId,  # 方案 id
    "sj": "0_0",
    "kkxsh": "",
    "kclbdm": "",
    "kclbdm2": "",
    "inputCode": "",
    "tokenValue": ""
}

http_head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 "
                  "Safari/537.36 Edg/105.0.1343.33"
}

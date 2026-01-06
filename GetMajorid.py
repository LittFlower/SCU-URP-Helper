import requests
import re
from UserLogin import userlogin
from staticINF import http_head, courseSelect_url, UserName, PassWord, set_major_id, print_log

def fetch_major_id(auto_save: bool = True):
    """
    Log in with configured credentials, fetch the course selection page,
    and try to extract the major_id (fajhh). Optionally auto-save it.
    :param auto_save: when True, persist the detected major_id to config.
    :return: detected major_id string or None.
    """
    if not UserName or not PassWord:
        print_log("Please configure UserName and PassWord in config.json first.", "ERROR")
        return None

    print_log(f"Attempting login with account: {UserName} ...", "INFO")

    session = requests.session()

    try:
        session = userlogin(session)
    except SystemExit:
        print_log("Login stopped by system exit.", "ERROR")
        return None
    except Exception as e:
        print_log(f"登录发生异常: {e}", "ERROR")
        return None

    print_log("Login success, fetching course selection page to locate MajorId (fajhh)...", "INFO")

    try:
        response = session.get(courseSelect_url, headers=http_head)
        response.encoding = response.apparent_encoding  # 修正中文编码
        html_content = response.text

        patterns = [
            r'fajhh=(\d+)',                                   # [新增] 匹配 URL 参数 ?fajhh=12345
            r'name["\']fajhh["\']\s+value["\'](\d+)["\']',     # 匹配 input 标签 name在前
            r'value["\'](\d+)["\']\s+name["\']fajhh["\']',     # 匹配 input 标签 value在前
            r'fajhh\s*=\s*["\'](\d+)["\']',                   # 匹配 js 变量
            r'fajhh["\']?\s*:\s*["\']?(\d+)["\']?'            # 匹配 json 对象
        ]

        found_id = None
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                found_id = match.group(1)
                break

        if found_id:
            print_log(f"Found major_id (fajhh): {found_id}", "SUCCESS")
            if auto_save:
                saved_id = set_major_id(found_id)
                print_log(f"major_id persisted to config.json: {saved_id}", "SUCCESS")
            else:
                print_log(f"Update staticINF.py manually with MajorId: {found_id}", "INFO")
        else:
            print_log("Could not detect MajorId automatically; please check manually.", "ERROR")

        return found_id

    except Exception as e:
        print_log(f"Error while requesting course selection page: {e}", "ERROR")
        return None

if __name__ == "__main__":
    fetch_major_id()

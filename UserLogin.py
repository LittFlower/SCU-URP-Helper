from sys import exit
from staticINF import *

import hashlib
import re
from typing import Optional, Tuple
from urllib.parse import urljoin

import ddddocr
import requests


def _dump_debug_html(file_name: str, content: str) -> None:
    with open(file_name, "w", encoding="utf-8", errors="ignore") as html_file:
        html_file.write(content)


def _dump_debug_text(file_name: str, content: str) -> None:
    with open(file_name, "w", encoding="utf-8", errors="ignore") as text_file:
        text_file.write(content)


def _extract_form_action(page_text: str) -> str:
    match = re.search(
        r'(?is)<form[^>]*action=["\']([^"\']+)["\']',
        page_text,
    )
    if not match:
        return security_check_url

    return urljoin(login_url, match.group(1))


def _extract_hidden_inputs(page_text: str) -> dict[str, str]:
    hidden_inputs: dict[str, str] = {}
    for match in re.finditer(r'(?is)<input\b([^>]+)>', page_text):
        attrs = match.group(1)
        type_match = re.search(r'type=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        if not type_match or type_match.group(1).lower() != "hidden":
            continue

        name_match = re.search(r'name=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        if not name_match:
            continue

        value_match = re.search(r'value=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        hidden_inputs[name_match.group(1)] = value_match.group(1) if value_match else ""

    return hidden_inputs


def _extract_login_button_onclick(page_text: str) -> str:
    match = re.search(
        r'(?is)<input[^>]*id=["\']loginButton["\'][^>]*onclick=["\'](.*?)["\']',
        page_text,
    )
    if not match:
        return ""

    return match.group(1)


def _extract_token(page_text: str) -> str:
    patterns = (
        r'name=["\']tokenValue["\'][^>]*value=["\']([^"\']+)["\']',
        r'id=["\']tokenValue["\'][^>]*value=["\']([^"\']+)["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_login_error(page_text: str) -> str:
    known_errors = (
        "验证码错误",
        "token校验失败",
        "用户名或密码错误",
        "账号或密码错误",
        "用户名或密码不正确",
        "密码错误",
    )
    for error_text in known_errors:
        if error_text in page_text:
            return error_text

    generic_patterns = (
        r'(?s)<[^>]*class=["\'][^"\']*(?:error|alert)[^"\']*["\'][^>]*>(.*?)</[^>]+>',
        r'(?s)<font[^>]*color=["\']?red["\']?[^>]*>(.*?)</font>',
    )
    for pattern in generic_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if not match:
            continue

        message = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        if message:
            return message

    return ""


def _is_login_success(page_text: str, response_url: str) -> bool:
    return "退出系统" in page_text or "/student/" in response_url


def _md5_hex(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def _detect_password_rule(page_text: str) -> Tuple[Optional[str], str]:
    onclick_code = _extract_login_button_onclick(page_text)
    if not onclick_code:
        return None, ""

    normalized = re.sub(r"\s+", "", onclick_code)
    _dump_debug_text("debug_password_js.txt", onclick_code)

    double_md5_pattern = (
        r"hex_md5\(hex_md5\(\$\('#input_password'\)\.val\(\)(?:,'1\.8')?\)"
        r"(?:,'1\.8')?\)\+'\*'\+"
        r"hex_md5\(hex_md5\(\$\('#input_password'\)\.val\(\)(?:,'1\.8')?\)"
        r"(?:,'1\.8')?\)"
    )
    if re.search(double_md5_pattern, normalized, re.IGNORECASE):
        return "double_md5_pair", onclick_code

    legacy_md5_pattern = (
        r"hex_md5\(\$\('#input_password'\)\.val\(\)\+'\{Urp602019\}'\)"
        r"\+'\*'\+hex_md5\(\$\('#input_password'\)\.val\(\)\)"
    )
    if re.search(legacy_md5_pattern, normalized, re.IGNORECASE):
        return "legacy_magic_md5_pair", onclick_code

    if "hex_md5($('#input_password').val())" in normalized.lower():
        return "plain_md5", onclick_code

    return None, onclick_code


def _get_password_rules(page_text: str) -> list[str]:
    rules: list[str] = []
    detected_rule, _ = _detect_password_rule(page_text)
    if detected_rule:
        rules.append(detected_rule)

    # 历史规则保底，避免登录页脚本小改后完全失效。
    for fallback_rule in ("double_md5_pair", "legacy_magic_md5_pair", "plain_md5"):
        if fallback_rule not in rules:
            rules.append(fallback_rule)

    return rules


def _build_password(password_plain: str, rule_name: str) -> str:
    if rule_name == "double_md5_pair":
        double_md5 = _md5_hex(_md5_hex(password_plain))
        return double_md5 + "*" + double_md5

    if rule_name == "legacy_magic_md5_pair":
        magic_str = "{Urp602019}"
        return _md5_hex(password_plain + magic_str) + "*" + _md5_hex(password_plain)

    if rule_name == "plain_md5":
        return _md5_hex(password_plain)

    raise ValueError(f"Unsupported password rule: {rule_name}")


def userlogin(_http_main: requests.session) -> requests.session:
    """Log in to the SCU URP system and keep the session cookies."""
    ocr: ddddocr.DdddOcr = ddddocr.DdddOcr()
    login_attempts = 0
    password_rule_index = 0

    while login_attempts < 100:
        res = _http_main.get(login_url, headers=http_head)
        if res.status_code != 200:
            print_log(f"[登录未成功]：无法打开登录页，状态码={res.status_code}")
            login_attempts += 1
            continue
        _dump_debug_html("debug_login_page.html", res.text)

        action_url = _extract_form_action(res.text)
        hidden_inputs = _extract_hidden_inputs(res.text)
        password_rules = _get_password_rules(res.text)
        detected_password_rule, onclick_code = _detect_password_rule(res.text)
        if onclick_code and not detected_password_rule:
            print_log("[登录提示]：已抓到登录页加密 JS，但未完全识别，先按内置兼容规则尝试")
        if password_rule_index >= len(password_rules):
            password_rule_index = 0
        password_rule = password_rules[password_rule_index]

        token = _extract_token(res.text)
        if not token:
            print_log("[登录未成功]：未能从登录页提取 token，教务系统页面结构可能已经变化")
            exit(-1)

        code_photo = _http_main.get(captcha_url, headers=http_head)
        with open("code.jpg", "wb") as photo:
            photo.write(code_photo.content)

        captcha_code = ocr.classification(code_photo.content)
        current_login_data = dict(hidden_inputs)
        current_login_data["j_username"] = UserName
        current_login_data["tokenValue"] = token
        current_login_data["j_password"] = _build_password(PassWord, password_rule)
        current_login_data["j_captcha"] = captcha_code

        login_headers = dict(http_head)
        login_headers["Referer"] = login_url
        login_headers["Origin"] = "http://zhjw.scu.edu.cn"

        res = _http_main.post(
            action_url,
            data=current_login_data,
            headers=login_headers,
        )
        _dump_debug_html("debug_login_response.html", res.text)

        if _is_login_success(res.text, res.url):
            print_log("[已成功登录]：成功登录系统")
            return _http_main

        error_message = _extract_login_error(res.text)
        if error_message == "验证码错误":
            print_log("[登录未成功]：验证码不正确，自动进行下一次尝试")
            login_attempts += 1
            continue
        if error_message and "密码" in error_message and password_rule_index + 1 < len(password_rules):
            print_log(
                f"[登录提示]：当前规则 `{password_rule}` 返回密码错误，切换到备用规则重试"
            )
            password_rule_index += 1
            continue
        if error_message:
            print_log(f"[登录未成功]：{error_message}")
            exit(-1)

        print_log(
            f"[登录未成功]：未识别的登录响应，状态码={res.status_code}，返回地址={res.url}"
        )
        exit(-1)

    print_log("[登录未成功]：验证码连续识别失败次数过多")
    exit(-1)

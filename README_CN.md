# SCU-Urp-Helpers

## 选择语言 / Choose Language

[English](README.md) | [中文](README_CN.md)

---

## 警告

**使用此仓库即表示您已完全阅读本README，并同意对您的行为及其后果负责。此项目的开发者不对使用本项目产生的任何结果负责。**

**鉴于本项目的特殊性，开发者可能会随时停止更新或删除此仓库。**

## 快速开始

### 下载

- 使用Git克隆仓库：`git clone git@github.com:LittFlower/SCU-Urp-Helpers.git`
- 或直接下载仓库。

### 依赖

本项目依赖以下Python包：

- requests
- ddddocr
- hashlib
- json
- sys

在运行 `Main.py` 之前，首先安装这些包（注意，有些包是 python 内置的，请区分之）。

### 配置

1. 复制（或者重命名） `staticINF.py.example` 为 `staticINF.py`，建议每次 `git pull` 之后重新执行此操作来确保该文件的一致性。
2. 打开 `staticINF.py` 并更新 `username`，`password` 和 `MajorId` 字段信息。
 - **hint: 如果你不知道怎么确定 `MajorId`，请来 github repo 看看 closed issue**

3. 运行脚本：

```bash
python Main.py
```
另一种使用方法是通过虚拟环境运行 `Main.py`。您可以使用 `poetry` 或 `pdd` 来管理您的包。

使用 `poetry` 运行脚本：

```bash
poetry run python Main.py
```

### 运行脚本

执行 `python Main.py` 后，系统会自动登录并进入课程选择页面。您可以根据指引搜索相关课程。例如，搜索"大数据"会显示与大数据相关的课程：

```plaintext
请输入一个课程名（关键词）或输入 'done' 完成选课：大数据
[成功获取课表]：成功进入课表页面，正在读取教务处课表列表，请耐心等待
1. 314011020_01 大数据分析及隐私保护 杨进*  60
2. 402893020_01 财务大数据分析与实验 刘静*  7
3. 402893020_02 财务大数据分析与实验 刘静*  12
```

然后，您可以输入相应编号将课程添加到选课列表。完成选课后，输入 `done` 开始自动选课。

### 邮件通知功能

脚本包含可选的邮件通知功能，当成功抢到课程时会自动发送通知邮件。使用方法：

1. 在 `run.sh` 中启用邮件通知：
```bash
export SEND_MAIL="True"  # 设置为 "True" 启用邮件通知
```

2. 在 `run.sh` 中设置邮箱配置：
```bash
export SMTP_HOST="smtp.126.com"           # 邮箱服务器地址
export SMTP_PORT="465"                    # 邮箱服务器端口
export SMTP_USER="你的126邮箱地址"         # 邮箱地址
export SMTP_PASSWORD="你的授权码"          # 邮箱授权码
```

3. 安装所需的Python包：
```bash
pip install redmail
```

4. 确保你的126邮箱已开启SMTP服务。

通知邮件将包含以下信息：
- 课程名称
- 课程编号
- 课序号

注意事项：
- 需要使用126邮箱的授权码，而不是登录密码
- 如果发送邮件失败，会在控制台打印错误信息，但不会影响抢课流程
- 默认情况下，通知邮件会发送到用于SMTP的同一个邮箱地址
- 你可以通过设置 `SEND_MAIL="False"` 来禁用邮件通知功能

## 贡献

欢迎任何人对本仓库做出贡献。

如果您有任何问题，请在仓库中发起issue进行提问。

## 注意

本仓库仅用于学习目的。提供的代码包含最小的示例，仅供学习使用。由于开发者的学术压力和个人精力限制，本项目不承诺定期更新。

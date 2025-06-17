#!/bin/bash

# 设置账户信息
# 请修改以下信息为你的账号信息
export USERNAME="2023141460xxx"  # 学号
export PASSWORD="123456"     # 密码
export MAJOR_ID="10646"         # 专业号
# 专业号说明：
# - 网安：10185
# - 降转网安：202403190401
# - 化学大类：10574
# - 计算机大类：10646
# - 化学拔尖：10587
export SLEEP_TIME=5             # 查找课程的间隔时间（秒），建议设置高一点更安全

# 设置邮件功能
export SEND_MAIL="True"        # 是否启用邮件通知功能（True/False）

# 设置邮箱信息（仅在启用邮件功能时需要）
export SMTP_HOST="smtp.126.com"           # 邮箱服务器地址
export SMTP_PORT="465"                    # 邮箱服务器端口，默认为465
export SMTP_USER="xxxxxx@126.com"        # 邮箱地址
export SMTP_PASSWORD="xxxxxxxxxxxxxxx"   # 邮箱授权码（不是登录密码）(以126为例，应该为16位。在邮箱安全中心可开启)

# 运行抢课脚本
python Main.py 
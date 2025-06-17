# SCU-Urp-Helpers

## Choose Language / 选择语言

[English](README.md) | [中文](README_CN.md)

---

## Warning

**By using this repository, you acknowledge that you have fully read the README and agree to take responsibility for your actions and any consequences thereof. The developers of this project are not liable for any outcomes resulting from its use.**

**Due to the nature of this project, the developer may stop updating or delete this repository at any time.**

## Quick Start

### Download

- Clone the repository using Git: `git clone git@github.com:LittFlower/SCU-Urp-Helpers.git`
- Alternatively, download the repository directly.

### Dependencies

This project requires the following Python packages:

- requests
- ddddocr
- hashlib
- json
- sys

Install these packages before running `Main.py`, (note that some packages are built-in to Python, please distinguish them).

### Configuration

1. Copy (or rename) `staticINF.py.example` to `staticINF.py`. It is recommended to perform this operation again after each `git pull` to ensure the consistency of the file.
2. Open `staticINF.py` and update the `username`, `password`, and `MajorId` field information.
    - **Hint: If you don't know how to determine `MajorId`, please check the closed issue on the GitHub repo**

Another way to use the project is by running `Main.py` in a virtual environment. You can manage your packages using `poetry` or `pdd`.

To run the script with `poetry`:

```bash
poetry run python Main.py
```

### Running the Script

After executing `python Main.py`, the system will automatically log in and navigate to the course selection page. You can search for relevant courses by entering keywords. For example, searching for "大数据" will display courses related to big data:

```plaintext
请输入一个课程名（关键词）或输入 'done' 完成选课：大数据
[成功获取课表]：成功进入课表页面，正在读取教务处课表列表，请耐心等待
1. 314011020_01 大数据分析及隐私保护 杨进*  60
2. 402893020_01 财务大数据分析与实验 刘静*  7
3. 402893020_02 财务大数据分析与实验 刘静*  12
```

Then, you can enter the corresponding number to add a course to your selection list. Once you have finished selecting courses, enter `done` to start the automated course registration process.

### Email Notification Feature

The script includes an optional email notification feature that will send you an email when a course is successfully selected. To use this feature:

1. Enable email notifications in `run.sh`:
```bash
export SEND_MAIL="True"  # Set to "True" to enable email notifications
```

2. Set up email configuration in `run.sh`:
```bash
export SMTP_HOST="smtp.126.com"           # Email server address
export SMTP_PORT="465"                    # Email server port
export SMTP_USER="your_126_email@126.com" # Email address
export SMTP_PASSWORD="your_auth_code"     # Email authorization code
```

3. Install the required Python package:
```bash
pip install redmail
```

4. Make sure your 126 email account has SMTP service enabled.

The notification email will include:
- Course name
- Course ID
- Class number

Important notes:
- You need to use the authorization code from your 126 email account, not your login password
- If email sending fails, an error message will be printed to the console, but it won't affect the course selection process
- By default, notifications are sent to the same email address used for SMTP
- You can disable email notifications by setting `SEND_MAIL="False"` in `run.sh`

## Contributing

Contributions to this repository are welcome.

If you have any questions or issues, please open an issue in the repository.

## Note

This repository is for educational purposes only. The code provided contains minimal examples intended for learning. Due to academic commitments and personal constraints, the developer does not guarantee regular updates to this project.

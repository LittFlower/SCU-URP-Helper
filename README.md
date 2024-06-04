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

Install these packages before running `Main.py`.

### Configuration

1. Open `staticINF.py` and update the `username`, `password`, and `MajorId` fields with your information.
2. Run the script: `python Main.py`.

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

## Contributing

Contributions to this repository are welcome.

If you have any questions or issues, please open an issue in the repository.

## Note

This repository is for educational purposes only. The code provided contains minimal examples intended for learning. Due to academic commitments and personal constraints, the developer does not guarantee regular updates to this project.
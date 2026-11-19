# Day 0 · 环境搭建

## 跑通的命令
.\.venv\Scripts\python.exe day0_smoke.py

## 踩过的坑
1. `python day0_smoke.py` 报 ModuleNotFoundError → python 不是 venv 的
2. 规则：永远 `python -m pip install`，不用裸 pip
3. VS Code 集成终端要「选中解释器 + 重开终端」才激活

## 结论
API 调用 = HTTP POST + Bearer key + messages 数组，返回 choices[0].message.content
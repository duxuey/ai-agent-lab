# ai-agent-lab

AI Agent 实验与练习仓库。第 0–12 周的学习笔记、实验代码与 capstone 都在这里。

## 每天开工第一条命令

```powershell
.\.venv\Scripts\python.exe review_due.py
```

列出今天到期和逾期的复习卡（1/3/7/15/30 天间隔）。复习完标记：

```powershell
.\.venv\Scripts\python.exe review_due.py --done pip-python
```

## 目录结构

```
ai-agent-lab/
├─ notes/
│  ├─ capstone-brief.md      # 项目定义（决策记录，会持续更新）
│  ├─ day0.md                # 准备期笔记
│  ├─ baseline_*.md          # 基线探测结果
│  └─ cards/                 # 复习卡，文件名前缀 = 创建日
├─ samples/                  # 真实输入样本 / 评测集
├─ baseline.py               # 裸模型基线测试
├─ day0_smoke.py             # 第一次 API 调用
└─ review_due.py             # 复习卡调度
```

## 约定

- 装包永远用 `python -m pip install`
- 跑脚本永远用 `.\.venv\Scripts\python.exe`（不依赖激活）
- `.env` 不进版本库，`.env.example` 进

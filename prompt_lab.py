"""prompt_lab.py — 同一任务 5 版 prompt，对比输出差异

固定任务：从一份会议记录里提取待办事项。
每版只加一个变量，看它带来什么变化。
"""

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent

for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

MEETING = """产品周会 2026-11-26

张伟：上周的登录改版已经上线，灰度 10%，目前没有异常。
李娜：用户反馈改版后找不到"退出"按钮，需要确认是不是样式覆盖导致的。这个我来跟。
张伟：下周三之前能不能给个结论？
李娜：可以，11 月 30 日前。
王强：支付回调的日志缺失问题还没修，依赖运维那边开放权限。
张伟：运维权限谁去推？
王强：我去找陈明，本周内搞定。
李娜：另外，帮助中心的老文章有一批链接失效了，需要有人扫一遍。
张伟：这个先记着，下周排期再定。
王强：对，还有压测报告也没人写。
张伟：散会。
"""

PROMPTS = {
    "V1 含糊版": "帮我整理一下这段会议记录。",
    "V2 只给任务": "从下面的会议记录里提取待办事项。",
    "V3 加角色": "你是一名项目经理助理。从下面的会议记录里提取待办事项。",
    "V4 加约束": (
        "你是一名项目经理助理。从下面的会议记录里提取待办事项，"
        "每条包含：待办内容、责任人、截止时间。"
        "原文没有的信息写「未提及」，绝对不要猜测。"
    ),
    "V5 加格式": (
        "你是一名项目经理助理。从下面的会议记录里提取待办事项，"
        "每条包含：待办内容、责任人、截止时间。"
        "原文没有的信息写「未提及」，绝对不要猜测。"
        "只输出 markdown 表格，四列：待办 | 责任人 | 截止时间 | 原文依据（逐字摘抄）。"
        "不要输出表格以外的任何文字。"
    ),
}


def ask(system_prompt, meeting):
    r = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "user", "content": system_prompt + "\n\n会议记录：\n" + meeting},
        ],
        temperature=0,
        max_tokens=800,
        extra_body={"thinking": {"type": "disabled"}},
    )
    return (r.choices[0].message.content or "").strip()


parts = ["# day05 · 5 版 prompt 对比\n"]
summary = []

for name, prompt in PROMPTS.items():
    text = ask(prompt, MEETING)
    rows = [ln for ln in text.splitlines() if ln.strip()]
    has_table = "|" in text
    parts.append(f"## {name}\n\n**prompt：** {prompt}\n\n```\n{text}\n```\n")
    summary.append((name, len(text), len(rows), has_table))
    print(f"\n{'=' * 12} {name} {'=' * 12}")
    print(text)

print("\n" + "=" * 40)
print(f"{'版本':<12}{'字符':>6}{'行数':>6}{'含表格':>8}")
for name, chars, rows, table in summary:
    print(f"{name:<12}{chars:>6}{rows:>6}{str(table):>8}")

out = ROOT / "notes" / "w1" / "day05_outputs.md"
out.write_text("\n".join(parts), encoding="utf-8")
print("\n已写入", out)

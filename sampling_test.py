"""sampling_test.py — 同一 prompt，多组采样参数，每组跑 3 次

关键点：
1. deepseek-flash 是推理模型，会先消耗「思考」token；max_tokens 是思考+正文的总预算，
   给小了会得到 finish_reason="length" 且 content 为空。
2. 做采样实验时关掉思考（thinking: disabled），避免思考的随机性掩盖 temperature 的作用。
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

PROMPT = (
    "给下面这段产品描述起 3 个标题，每个不超过 12 个字：\n"
    "一个能自动整理会议纪要并提取待办事项的工具。"
)

CONFIGS = [
    ("T=0      ", {"temperature": 0}),
    ("T=0 重复 ", {"temperature": 0}),
    ("T=0.7    ", {"temperature": 0.7}),
    ("T=1.0    ", {"temperature": 1.0}),
    ("T=1.5    ", {"temperature": 1.5}),
    ("T=0.7 p.9", {"temperature": 0.7, "top_p": 0.9}),
    ("T=1.5 p.5", {"temperature": 1.5, "top_p": 0.5}),
]


def run(cfg):
    r = client.chat.completions.create(
        model="deepseek-flash",
        messages=[{"role": "user", "content": PROMPT}],
        max_tokens=200,
        extra_body={"thinking": {"type": "disabled"}},
        **cfg,
    )
    return (r.choices[0].message.content or "").strip(), r.choices[0].finish_reason


lines = [
    "# day03 · 采样参数实验",
    "",
    f"prompt：{PROMPT}",
    "",
    "| 参数 | finish | 第1次 | 第2次 | 第3次 | 唯一数 |",
    "|---|---|---|---|---|---|",
]

for label, cfg in CONFIGS:
    outs, reasons = [], set()
    for _ in range(3):
        text, reason = run(cfg)
        outs.append(text)
        reasons.add(reason)
    uniq = len(set(outs))
    cells = [o.replace("\n", " / ").replace("|", "｜")[:70] or "(空)" for o in outs]
    lines.append(
        f"| {label} | {'/'.join(sorted(reasons))} | " + " | ".join(cells) + f" | {uniq}/3 |"
    )
    print(f"{label} finish={'/'.join(sorted(reasons))} 唯一={uniq}/3")

lines += [
    "",
    "## 结论（待填）",
    "",
    "1. ",
    "2. ",
    "3. ",
]
out = ROOT / "notes" / "w1" / "day03_runs.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("已写入", out)

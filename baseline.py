"""baseline.py — 对 samples/news.txt 做一次"裸模型"基线测试

用法：
    .\.venv\Scripts\python.exe baseline.py
输出：
    notes/baseline_A_naive.md        朴素问法
    notes/baseline_B_constrained.md  加约束问法
"""

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent

# 读 .env
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

news = (ROOT / "samples" / "news.txt").read_text(encoding="utf-8")

PROMPT_A = (
    "下面是今天抓到的 10 条 AI 资讯（标题 + 摘要）：\n\n"
    + news
    + "\n\n"
    "请：\n"
    "1. 选出最重要的 3 条，说明为什么重要\n"
    "2. 为这 3 条各写一段 80 字左右的中文摘要\n"
    "3. 同一件事的多条请合并\n"
)

PROMPT_B = (
    "下面是今天抓到的 10 条 AI 资讯（标题 + 摘要）：\n\n"
    + news
    + "\n\n"
    "请输出一个 JSON 对象，不要任何解释文字，结构如下：\n"
    "{\n"
    '  "items": [\n'
    "    {\n"
    '      "title": "合并后的标题（中文）",\n'
    '      "source_ids": [原始条目序号],\n'
    '      "why_important": "为什么重要，一句话，必须基于原文",\n'
    '      "summary": "80 字以内摘要",\n'
    '      "evidence": "摘要所依据的原文片段，逐字引用，不得改写",\n'
    '      "confidence": "high | medium | low"\n'
    "    }\n"
    "  ],\n"
    '  "duplicates_merged": 0,\n'
    '  "skipped": [{"id": 序号, "reason": "为什么没选"}]  '
    "\n}\n\n"
    "硬性约束：\n"
    "1. 只选 3 条；同一件事的多条必须合并为一条，source_ids 里列出全部序号\n"
    "2. summary 只能使用原文中出现的事实，禁止补充背景知识\n"
    "3. evidence 必须逐字摘抄原文，找不到依据就写「原文未说明」\n"
    "4. 输出必须是合法 JSON，能被 json.loads 解析\n"
)

PROMPTS = {
    "A_naive": PROMPT_A,
    "B_constrained": PROMPT_B,
}

for name, prompt in PROMPTS.items():
    resp = client.chat.completions.create(
        model="deepseek-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    text = resp.choices[0].message.content or ""

    out = ROOT / "notes" / f"baseline_{name}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8")

    print(f"\n{'=' * 20} {name} {'=' * 20}")
    print(text)
    print(f"\n[用量] {resp.usage}")
    print(f"[已保存] {out}")

# 顺手检查 B 是不是合法 JSON —— 这本身就是一条评测指标
import json

b_text = (ROOT / "notes" / "baseline_B_constrained.md").read_text(encoding="utf-8")
try:
    json.loads(b_text.strip().removeprefix("```json").removesuffix("```").strip())
    print("\n[JSON 校验] 通过")
except Exception as e:
    print(f"\n[JSON 校验] 失败：{e}")
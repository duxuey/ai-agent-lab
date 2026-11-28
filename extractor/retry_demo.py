"""retry_demo.py — 故意制造校验失败，验证"错误回灌重试"是否有效

做法：schema 要求 priority 字段（高/中/低），但 system prompt 里完全不提。
第一次输出必然缺字段 → 触发 ValidationError → 错误回灌 → 看第二次能否补齐。
"""

import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent

for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")


class StrictItem(BaseModel):
    todo: str
    owner: str
    due: str
    priority: str = Field(pattern="^(高|中|低)$")   # prompt 里不提这个


class StrictResult(BaseModel):
    items: list[StrictItem]


SYSTEM = """你是信息抽取器，只输出 JSON。
输出结构：{"items": [{"todo": "...", "owner": "...", "due": "..."}]}
owner 和 due 原文没写就填「未提及」。
"""

TEXT = """张伟：登录改版灰度 10%，没有异常。
李娜：退出按钮问题我来跟，11 月 30 日前给结论。
王强：支付回调日志缺失，我去找陈明要权限，本周内搞定。"""

messages = [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": f"抽取待办：\n\n{TEXT}"},
]

for attempt in range(1, 4):
    r = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        temperature=0,
        max_tokens=800,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = (r.choices[0].message.content or "").strip()
    print(f"\n--- 第 {attempt} 次 ---")
    try:
        data = json.loads(raw)
        result = StrictResult.model_validate(data)
        print("校验通过：")
        for it in result.items:
            print(f"  {it.todo} | {it.owner} | {it.due} | {it.priority}")
        break
    except (json.JSONDecodeError, ValidationError) as e:
        err = str(e).replace("\n", " ")[:200]
        print(f"失败：{err}")
        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content": f"输出不合法：{err}\n请修正后只输出合法 JSON。"})

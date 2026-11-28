"""extract.py — 抽取待办，带 schema 校验与失败重试

流程：调 API → json.loads → Pydantic 校验 → 失败则把错误回灌给模型重试。
"""

import json
import os
import sys
from pathlib import Path

from pydantic import ValidationError

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent

for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI

from extractor.schema import ExtractionResult

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

SYSTEM = """你是信息抽取器，只输出 JSON，不要 markdown 代码块，不要任何解释文字。

输出结构：
{"items": [{"todo": "待办内容", "owner": "责任人", "due": "截止时间", "evidence": "逐字摘抄的原文依据"}], "note": "补充说明"}

规则：
1. owner 和 due 原文没写就填「未提及」，不要猜测、不要推断。
2. evidence 必须从原文逐字摘抄，不得改写、不得拼接不相邻的句子。
3. 一段原文里有多条待办就输出多条；没有待办就输出空数组。
"""

MAX_ATTEMPTS = 3


def extract_once(text: str):
    """返回 (结果或None, 尝试次数, 最后一次错误, 原始输出)"""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"从下面的内容里抽取待办：\n\n{text}"},
    ]
    last_err, raw = "", ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        r = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            temperature=0,
            max_tokens=1500,
            response_format={"type": "json_object"},
            extra_body={"thinking": {"type": "disabled"}},
        )
        raw = (r.choices[0].message.content or "").strip()
        try:
            data = json.loads(raw)
            result = ExtractionResult.model_validate(data)
            return result, attempt, "", raw
        except json.JSONDecodeError as e:
            last_err = f"JSON 解析失败：{e}"
        except ValidationError as e:
            last_err = f"JSON 校验失败：{e.errors()[:3]}"

        # 把错误回灌，让模型自己修
        messages.append({"role": "assistant", "content": raw})
        messages.append(
            {"role": "user", "content": f"你的输出不合法：{last_err}\n请修正，只输出合法 JSON。"}
        )
    return None, MAX_ATTEMPTS, last_err, raw


def load_inputs(path: Path):
    blocks = []
    for chunk in path.read_text(encoding="utf-8").split("\n### "):
        chunk = chunk.strip()
        if chunk:
            blocks.append(chunk)
    return blocks


def main():
    inputs = load_inputs(Path(__file__).parent / "inputs.txt")
    rows = []
    for i, text in enumerate(inputs, 1):
        result, attempts, err, raw = extract_once(text)
        ok = result is not None
        n_items = len(result.items) if result else 0
        rows.append((i, ok, attempts, n_items, err))
        print(f"[{i:02d}] ok={ok} 尝试={attempts} 条目={n_items} {err[:80]}")

    ok_count = sum(1 for r in rows if r[1])
    avg_attempts = sum(r[2] for r in rows) / len(rows)
    print(f"\n合法率 {ok_count}/{len(rows)}  平均尝试 {avg_attempts:.2f}")

    lines = [
        "# day06 · 结构化输出实测",
        "",
        f"样本 {len(rows)} 条，合法率 {ok_count}/{len(rows)}，平均尝试 {avg_attempts:.2f}",
        "",
        "| # | 成功 | 尝试次数 | 条目数 | 错误 |",
        "|---|---|---|---|---|",
    ]
    for i, ok, attempts, n, err in rows:
        lines.append(f"| {i} | {'✓' if ok else '✗'} | {attempts} | {n} | {err[:60]} |")
    out = ROOT / "notes" / "w1" / "day06_runs.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("已写入", out)


if __name__ == "__main__":
    main()

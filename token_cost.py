"""token_cost.py — 同一批文本，不同 tokenizer 下的 token 数对照

用法：
    python token_cost.py          # 用 tiktoken 本地计数（两种 tokenizer）
    python token_cost.py --api    # 用 DeepSeek 真实 usage 计数（需要 .env）
"""

import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent

SAMPLES = {
    "中文": "大语言模型的上下文窗口决定了它一次能看多少内容，超出部分会被截断。",
    "英文": "The context window of a large language model determines how much content it can see at once.",
    "代码": 'def add(a, b):\n    return a + b\n',
    "JSON": json.dumps(
        {"model": "deepseek-flash", "messages": [{"role": "user", "content": "你好"}]},
        ensure_ascii=False,
    ),
    "混合": "请把这段话翻译成英文：今天天气不错。",
}

WIDTH = 16


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8-sig").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def count_tiktoken():
    try:
        import tiktoken
    except ImportError:
        print("缺少依赖，先装：python -m pip install tiktoken -i https://pypi.tuna.tsinghua.edu.cn/simple")
        return None

    encoders = {}
    for name in ("cl100k_base", "o200k_base"):
        try:
            encoders[name] = tiktoken.get_encoding(name)
        except Exception as e:  # 下载词表失败等
            print(f"[跳过 {name}] {e}")
    if not encoders:
        return None

    rows = []
    for label, text in SAMPLES.items():
        row = {"样本": label, "字符": len(text)}
        for name, enc in encoders.items():
            row[name] = len(enc.encode(text))
        rows.append(row)
    return list(encoders), rows


def count_api():
    load_env()
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    rows = []
    for label, text in SAMPLES.items():
        r = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": text}],
            max_tokens=1,
            temperature=0,
        )
        rows.append({"样本": label, "字符": len(text), "真实 prompt_tokens": r.usage.prompt_tokens})
    return ["真实 prompt_tokens"], rows


def print_table(cols, rows):
    head = f"{'样本':<8}{'字符':>8}  " + "".join(f"{c:>16}" for c in cols)
    print(head)
    print("-" * len(head))
    for row in rows:
        last = row[cols[-1]]
        ratio = f"{row['字符'] / last:.2f}" if last else "-"
        line = f"{row['样本']:<8}{row['字符']:>6}" + "".join(f"{row[c]:>{WIDTH}}" for c in cols) + f"{ratio:>12}"
        print(line)


def main():
    use_api = "--api" in sys.argv
    result = count_api() if use_api else count_tiktoken()
    if not result:
        return 1
    cols, rows = result
    print_table(cols, rows)
    print("\n注：字符/token 越大，该语言在这套分词器里越“省”。")
    if use_api:
        print("注：prompt_tokens 含消息格式开销（约 8–10 token），比纯文本计数略高。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
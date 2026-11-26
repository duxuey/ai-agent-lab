import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent

for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

history = [{"role": "system", "content": "你是一个简洁的中文助手。"}]
total = 0
turns = 0

while True:
    try:
        user = input("\n你> ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not user:
        continue
    if user == "/clear":
        history = history[:1]
        total = 0
        turns = 0
        print("[已清空历史]")
        continue
    if user in ("/exit", "/quit"):
        break

    history.append({"role": "user", "content": user})

    stream = client.chat.completions.create(
        model="deepseek-flash",
        messages=history,
        stream=True,
        extra_body={
            "thinking": {"type": "disabled"},
            "stream_options": {"include_usage": True},
        },
    )

    print("AI> ", end="", flush=True)
    reply = ""
    usage = None
    for chunk in stream:
        # 开了 include_usage 后，最后一个 chunk 只有 usage、没有 choices
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            reply += delta
            print(delta, end="", flush=True)
        if chunk.usage:
            usage = chunk.usage
    print()

    history.append({"role": "assistant", "content": reply})

    turns += 1
    if usage:
        turn_tokens = usage.prompt_tokens + usage.completion_tokens
        total += turn_tokens
        print(
            f"[第 {turns} 轮] prompt {usage.prompt_tokens} + completion {usage.completion_tokens}"
            f" = {turn_tokens} ｜ 累计 {total} ｜ 历史 {len(history)} 条"
        )

print(f"\n本次共 {turns} 轮，累计 {total} token，平均 {total // turns if turns else 0}/轮")

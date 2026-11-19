import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# 极简 .env 读取，只为不引入额外依赖
env = Path(".env")
if env.exists():
    for line in env.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

resp = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": "你是一个简洁的助教。"},
        {"role": "user", "content": "用一句话解释什么是 token。"},
    ],
)

print(resp.choices[0].message.content)
print("用量:", resp.usage)
import os
from pathlib import Path

for line in Path(".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
stream = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role": "user", "content": "数到五"}],
    stream=True,
    extra_body={"thinking": {"type": "disabled"}},
)
for c in stream:
    d = c.choices[0].delta.content
    if d:
        print(d, end="", flush=True)
print()
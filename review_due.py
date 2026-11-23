# -*- coding: utf-8 -*-
"""review_due.py — 按 1/3/7/15/30 天间隔管理复习卡

用法：
    python review_due.py                     列出今天到期和逾期的卡
    python review_due.py --done <关键词...>   标记已复习，排下一次
    python review_due.py --reset <关键词...>  答错/忘了：从头再走一轮
    python review_due.py --all               看所有卡的状态
"""

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "notes" / "cards"
STATE = CARDS / ".review.json"
STEPS = [1, 3, 7, 15, 30]


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    CARDS.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def date_from_name(p):
    m = re.match(r"(\d{4}-\d{2}-\d{2})", p.name)
    return date.fromisoformat(m.group(1)) if m else None


def sync(state):
    files = sorted(p for p in CARDS.glob("*.md"))
    names = {p.name for p in files}
    for p in files:
        if p.name in state:
            continue
        d = date_from_name(p)
        if d:
            state[p.name] = {
                "created": d.isoformat(),
                "step": 0,
                "next": (d + timedelta(days=STEPS[0])).isoformat(),
            }
    for gone in [k for k in state if k not in names]:
        del state[gone]
    return files


def fmt(name):
    return name[:-3] if name.endswith(".md") else name


def pick(state, keys):
    out = []
    for key in keys:
        hit = [n for n in state if key in n]
        if not hit:
            print(f"[未找到] {key}")
        out.extend(hit)
    return out


def main():
    args = sys.argv[1:]
    today = date.today()
    state = load_state()
    sync(state)

    if args and args[0] in ("--done", "--reset"):
        keys = args[1:]
        if not keys:
            print("用法：python review_due.py --done|--reset <文件名关键词 ...>")
            return 1
        mode = args[0]
        hit = 0
        for name in pick(state, keys):
            item = state[name]
            if mode == "--reset":
                item["step"] = 0
                nxt = today + timedelta(days=STEPS[0])
                item["next"] = nxt.isoformat()
                print(f"[重来] {fmt(name)}  下次 {nxt.isoformat()}")
            else:
                item["step"] += 1
                if item["step"] >= len(STEPS):
                    item["next"] = None
                    print(f"[完成] {fmt(name)} 已走完 5 次复习")
                else:
                    nxt = today + timedelta(days=STEPS[item["step"]])
                    item["next"] = nxt.isoformat()
                    print(f"[已记录] {fmt(name)} 第 {item['step']}/5 次，下次 {nxt.isoformat()}")
            hit += 1
        save_state(state)
        return 0 if hit else 1

    if args and args[0] == "--all":
        for name in sorted(state):
            it = state[name]
            nxt = it["next"] or "已走完"
            print(f"{fmt(name):45s} 第{it['step']}/5 次  下次 {nxt}")
        return 0

    due = []
    for name, it in state.items():
        if it["next"] is None:
            continue
        nxt = date.fromisoformat(it["next"])
        if nxt <= today:
            due.append((nxt, name, it))

    if not due:
        print(f"今天没有到期卡片（{today.isoformat()}）")
        upcoming = sorted(
            (date.fromisoformat(it["next"]), n) for n, it in state.items() if it["next"]
        )[:3]
        for d, n in upcoming:
            print(f"  下次：{d.isoformat()}  {fmt(n)}")
        return 0

    print(f"到期 {len(due)} 张（{today.isoformat()}）\n")
    for nxt, name, it in sorted(due):
        late = (today - nxt).days
        flag = f"逾期 {late} 天" if late else "今天"
        print(f"[{flag}] 第 {it['step'] + 1}/5 次  {fmt(name)}")
    print("\n复习完： python review_due.py --done <关键词...>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

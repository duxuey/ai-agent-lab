# day04 · 第一次 Chat API 调用（chat_cli）

日期：2026-11-26 ｜ 阶段：W1 D4

## 做了什么

`chat_cli/chat.py`：多轮历史 + 流式输出 + `/clear` + 每轮与累计 token 统计。

## 10 轮实测

| 指标 | 数值 |
|---|---|
| 第 1 轮 prompt_tokens | 13 |
| 第 10 轮 prompt_tokens | **809** |
| 倍数 | 约 62 倍 |
| 10 轮累计 | 4667 token |
| 平均每轮 | 467 token |
| 结束时历史条数 | 21（system + 10 轮问答）|

## 结论

1. **`prompt_tokens` 逐轮累加**：每轮都把前面全部历史重发一遍。
   第 10 轮的 prompt 是第 1 轮的 62 倍，而用户实际只多说了 9 句话。
2. **总成本随轮数接近平方增长**：轮数翻 4 倍，总 token 约翻 16 倍。
   按本次数据外推：40 轮约 7.5 万 token，100 轮约 47 万 token。
3. **平均成本会骗人**：10 轮平均 467/轮，但最后一轮单独就 866，
   占了总量的 18%。做预算要按"最长对话"估，不是按平均估。

## 两个实现层面的坑

1. **流式默认不返回 usage**：必须 `stream_options={"include_usage": True}`。
2. **开了 include_usage 后，最后一个 chunk 没有 choices，只有 usage**：
   所以必须写 `chunk.choices[0].delta.content if chunk.choices else None`，
   否则 `IndexError`。流式协议里"收尾包"常常只带元数据。

## 下一步（W2）

历史不可能无限塞。要么按窗口截断，要么摘要压缩，要么检索式记忆——
这就是 W2「上下文工程」要解决的问题。

## 修正记录（2026-11-26 复盘时发现）

原文写"最后一个 chunk 只有 usage、没有 choices"，**实测不成立**。

DeepSeek 的收尾块：`choices` 有 1 个元素，`content=''`，`usage` 有值。
真正的厂商差异是：OpenAI 官方的 usage 块 `choices` 为空列表，DeepSeek 不为空。

所以 `if chunk.choices else None` 仍然要写，但理由是**跨厂商防御**，
不是"DeepSeek 会崩"。

**教训：** "OpenAI 兼容"兼容的是字段名，**不保证边界行为一致**。
换厂商、换版本时，第一件事是用最小脚本打印出首块和尾块的原始结构。

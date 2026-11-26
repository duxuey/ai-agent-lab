# 流式响应的收尾块（跨厂商差异）

**Q：** 流式遍历 chunk 时，收尾块和数据块有什么区别？

**A：** 收尾块带 `usage`（需要 `stream_options={"include_usage": True}` 才会给），
content 是空的。它的 `choices` 是否为空**取决于厂商**：

- OpenAI 官方：usage 块的 `choices` 是空列表
- DeepSeek 实测（2026-11-26）：`choices` 仍有 1 个元素，`content` 是空字符串 `''`

所以跨厂商必须写 `chunk.choices[0].delta.content if chunk.choices else None`，
否则换一家就 `IndexError`。

**Q：** 第一块 chunk 的 content 是什么？

**A：** DeepSeek 是 `''`（空串），OpenAI 常见是 `None`。
`if delta:` 同时过滤这两种，是防御式写法——防的是厂商差异，不是"第几轮"。

**一句话：** 兼容的字段名，不兼容的边界行为。

# 流式响应的最后一块只有 usage

**Q：** 打开 `stream_options={"include_usage": True}` 后，遍历 chunk 报 `IndexError`，为什么？

**A：** 最后的收尾 chunk 只带 `usage`，`choices` 是空列表，所以 `chunk.choices[0]` 越界。

**正确写法：**

```python
delta = chunk.choices[0].delta.content if chunk.choices else None
if chunk.usage:
    usage = chunk.usage
```

**通用规律：** 流式协议里，**数据包和元数据包是分开的**；结尾那一块常常没有内容。
接任何流式接口都要先问一句："收尾包长什么样？"

**一句话：** 最后一块不是内容，是账单。

# 推理模型的 max_tokens 是思考+正文的总预算

**Q：** 调用 deepseek-flash，返回的 `content` 是空字符串，`finish_reason="length"`，为什么？

**A：** 它是推理模型，先输出隐藏的思考再输出正文，而 `max_tokens` 限制的是**两者之和**。
预算给小时，token 全被思考用完，正文一个字都没轮到。

**判断方法：** 看 `usage.completion_tokens_details.reasoning_tokens`，
它接近 max_tokens 就是被思考吃掉了。

**处理：** 调大 `max_tokens`（留 3–5 倍余量），或
`extra_body={"thinking": {"type": "disabled"}}` 关掉思考。

**工程含义：** 推理模型的成本不只是"输出长度"，思考 token 也计费；
做 agent 时要按最坏情况估预算，而不是按最终答案长度估。

**一句话：** 空输出不一定是模型坏了，先看预算被谁吃了。

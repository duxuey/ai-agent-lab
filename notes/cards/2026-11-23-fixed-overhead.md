# 单次 prompt_tokens 不能比长度

**Q：** 为什么不能拿单次 `prompt_tokens` 比较两段不同长度的文本谁更费 token？

**A：** 每次请求有固定的对话模板开销（实测 DeepSeek 约 30 token），它和文本长度无关。
短文本里它占比极高，比例完全失真（18 字符的样例测出 41 token）。

**做法：** 把同一段文本乘 1/2/4/8 倍各请求一次，用 `(t8 - t1) / 7` 求每份的真实 token 数。

**一句话：** 先扣掉常数项，再谈比例。


"usage": {
    "prompt_tokens": 2434, --本次API调用中，作为输入提供给LLM的prompt（提示）部分所占用的token数量。
                           包括了所有发送给LLM的消息（System消 息、User消息等）的token总和。
    "completion_tokens": 694, --表示LLM生成的回复（completion）部分所占用的token数量。
                              仅包括LLM输出的文本的token数量，不包括prompt的token数量。
    "total_tokens": 3128 --本次API调用的总token消耗量。是prompt_tokens和completion_tokens的总和。
  }
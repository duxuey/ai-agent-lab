# pip 成功但 import 失败

**Q：** `pip install openai` 成功了，`python day0_smoke.py` 还是 `ModuleNotFoundError`，为什么？

**A：** 装包和运行用了两个不同的 Python 解释器。`pip` 属于 A，`python` 指向 B。
判断：`where python` 与 `python -m pip -V` 输出的是不是同一个路径。
根治：永远用 `python -m pip install`，或固定用 `.\.venv\Scripts\python.exe`。

## 现场验证（30 秒）

```powershell
where python
python -m pip -V
```
两个路径不一致，就是这张卡说的情况。

**一句话：** 装的、跑的、以为的，是三个不同的东西。

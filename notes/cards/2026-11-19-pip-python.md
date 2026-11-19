Q: pip install 成功了，python 脚本还是 ModuleNotFoundError，为什么？
A: 装包和运行用了两个不同的解释器。判断：where python 和 python -m pip -V 的路径是否一致。
   根治：永远用 python -m pip install，或固定用 .\.venv\Scripts\python.exe。
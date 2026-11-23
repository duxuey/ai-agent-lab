# 文件建了 git 看不到

**Q：** 文件明明创建了，`git` 完全看不到，第一步查什么？

**A：** `git check-ignore -v 文件名`。它会直接告诉你是**哪个文件的第几行、哪条规则**挡住的；没有输出就说明没被忽略，那就是路径不对或没 `add`。

## 现场验证（30 秒）

```powershell
"x" | Set-Content .env.local
git check-ignore -v .env.local
Remove-Item .env.local
```

## 常见坑

`.env.*` 会把 `.env.example` 一起忽略，需要在它**后面**加 `!.env.example` 放行（顺序不能反）。

**一句话：** 先问"谁在挡我"，再问"文件在不在"。

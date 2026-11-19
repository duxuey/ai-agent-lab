Q: 文件明明创建了，git 却完全看不到，第一步查什么？
A: git check-ignore -v 文件名。它会直接告诉你是哪一行规则、在哪个文件里挡住的。
   常见坑：.env.* 会把 .env.example 一起忽略，需要在后面加 !.env.example 放行。
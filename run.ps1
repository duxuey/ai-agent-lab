$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { python -m venv .venv }
$env:PYTHONUTF8 = "1"
& $py @args
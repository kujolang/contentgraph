@echo off
setlocal
set "ROOT=%~dp0"
if defined KUJO_BIN (
  set "KUJO_RUNTIME=%KUJO_BIN%"
) else (
  set "KUJO_RUNTIME=%ROOT%..\kujo\target\release\kujo.exe"
)
if not exist "%KUJO_RUNTIME%" (
  echo ContentGraph: Kujo runtime not found. Set KUJO_BIN. 1>&2
  exit /b 2
)
set "CONTENTGRAPH_KUJO_BIN=%KUJO_RUNTIME%"
cd /d "%ROOT%"
"%KUJO_RUNTIME%" run --untrusted --allow-fs-read --allow-fs-write --allow-fs-delete --allow-process-exec --allow-env-read --allow-clock --allow-random src/main.kujo -- %*

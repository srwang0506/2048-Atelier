@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
if exist "runtime\python.exe" (
  "runtime\python.exe" check_runtime.py
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" check_runtime.py
) else (
  echo Game runtime not found. Extract the entire portable ZIP, or run the game launcher first.
)
echo.
pause
popd

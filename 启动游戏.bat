@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
if exist "runtime\python.exe" goto portable
if exist ".venv\Scripts\python.exe" goto dependencies
set "ATELIER_PYTHON="
py -3.13 -c "import struct; assert struct.calcsize('P') == 8" >nul 2>&1
if not errorlevel 1 set "ATELIER_PYTHON=py -3.13"
if defined ATELIER_PYTHON goto create
py -3.12 -c "import struct; assert struct.calcsize('P') == 8" >nul 2>&1
if not errorlevel 1 set "ATELIER_PYTHON=py -3.12"
if defined ATELIER_PYTHON goto create
python -c "import sys,struct; assert (3,12) <= sys.version_info[:2] < (3,15) and struct.calcsize('P') == 8" >nul 2>&1
if not errorlevel 1 set "ATELIER_PYTHON=python"
if defined ATELIER_PYTHON goto create
echo Python 3.12-3.14 64-bit was not found.
echo Use the Windows portable package, or install Python from https://www.python.org/downloads/windows/
goto failed
:create
%ATELIER_PYTHON% -m venv .venv
if errorlevel 1 goto failed
:dependencies
".venv\Scripts\python.exe" -c "import sys,struct; assert (3,12) <= sys.version_info[:2] < (3,15) and struct.calcsize('P') == 8" >nul 2>&1
if errorlevel 1 (
  echo The .venv folder uses an incompatible Python. Rename it and try again.
  goto failed
)
".venv\Scripts\python.exe" check_runtime.py --dependencies >nul 2>&1
if not errorlevel 1 goto run
echo Preparing game dependencies. An internet connection is required on the first run.
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --only-binary=:all: -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" check_runtime.py --dependencies
if errorlevel 1 goto failed
:run
".venv\Scripts\python.exe" desktop_start.py %*
if errorlevel 1 goto failed
popd
exit /b 0
:portable
"runtime\python.exe" desktop_start.py %*
if errorlevel 1 goto failed
popd
exit /b 0
:failed
echo.
echo 2048 could not start. Read the error above, or run check-windows.bat for diagnostics.
pause
popd
exit /b 1

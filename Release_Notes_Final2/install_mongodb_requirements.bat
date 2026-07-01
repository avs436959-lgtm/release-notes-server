@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m pip install -r requirements.txt
  pause
  goto done
)

where python >nul 2>nul
if %errorlevel%==0 (
  python -m pip install -r requirements.txt
  pause
  goto done
)

echo Python bulunamadi.
echo Once Python 3 kur: https://www.python.org/downloads/
pause

:done

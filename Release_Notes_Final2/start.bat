@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 server.py
  if errorlevel 1 pause
  goto done
)

where python >nul 2>nul
if %errorlevel%==0 (
  python server.py
  if errorlevel 1 pause
  goto done
)

echo Python bulunamadi.
echo Bu veritabanli surumu calistirmak icin Python 3 kurulu olmali.
echo https://www.python.org/downloads/
pause

:done

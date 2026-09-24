@echo off
setlocal
cd /d "%~dp0"
echo ChatShift setup - text and local voice
echo Keep this window open until setup finishes.
set "CHATSHIFT_PY=%LocalAppData%\Programs\Python\Python313\python.exe"
if exist "%CHATSHIFT_PY%" goto install
py -3.13 -c "import sys" >nul 2>&1
if not errorlevel 1 goto launcher
echo Installing Python 3.13 from the Windows package manager...
winget install --id Python.Python.3.13 --exact --source winget --scope user --architecture x64
if errorlevel 1 goto failed
if exist "%CHATSHIFT_PY%" goto install
:launcher
py -3.13 install_chatshift.py
goto result
:install
"%CHATSHIFT_PY%" install_chatshift.py
:result
if errorlevel 1 goto failed
echo.
echo Setup complete. Use the ChatShift shortcut on your desktop.
pause
exit /b 0
:failed
echo.
echo Setup did not finish. See the error above. You can run this file again.
echo If Python could not be installed, install Python 3.13 from python.org.
echo If this folder is inside a ZIP, extract it first.
pause
exit /b 1

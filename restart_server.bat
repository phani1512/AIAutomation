@echo off
echo Stopping API server...
taskkill /F /FI "COMMANDLINE eq *api_server_modular.py*" 2>nul
timeout /t 2 /nobreak >nul

echo Starting API server...
cd /d "%~dp0"
start /B python src\main\python\api_server_modular.py

echo.
echo Server restarted! Wait 5 seconds for it to initialize.
echo Then refresh your browser and test again.
timeout /t 5 /nobreak

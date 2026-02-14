@echo off
pushd "%~dp0"
chcp 65001 > nul
echo.
echo ==========================================
echo   INVESTIGANDO ERRO 500 (SERVER ERROR)
echo ==========================================
echo.

if not exist venv_dev (
    echo [ERRO] Ambiente 'venv_dev' ainda nao foi criado!
    pause
    exit
)

venv_dev\Scripts\python.exe debug_error_500.py

echo.
pause

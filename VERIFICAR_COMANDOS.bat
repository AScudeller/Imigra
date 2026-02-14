@echo off
pushd "%~dp0"
chcp 65001 > nul
echo.
echo ==========================================
echo   VERIFICANDO COMANDOS DJANGO
echo ==========================================
echo.

if not exist venv_dev (
    echo [ERRO] Ambiente 'venv_dev' ainda nao foi criado!
    echo Execute o SETUP_LOCAL_DEV.bat primeiro.
    pause
    exit
)

:: Usa o caminho completo do python
venv_dev\Scripts\python.exe debug_commands.py

echo.
pause

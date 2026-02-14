@echo off
pushd "%~dp0"
chcp 65001 > nul
echo.
echo ==========================================
echo   TESTE MANUAL DO SERVIDOR DJANGO
echo ==========================================
echo.

if not exist venv_dev (
    echo [ERRO] Ambiente 'venv_dev' nao encontrado!
    pause
    exit
)

echo Iniciando o servidor... (Se der erro, ele vai aparecer abaixo)
echo.
venv_dev\Scripts\python.exe manage.py runserver 0.0.0.0:8000

echo.
echo SERVIDOR PAROU OU CAIU.
pause

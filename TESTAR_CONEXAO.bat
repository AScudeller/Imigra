@echo off
pushd "%~dp0"
chcp 65001 > nul
echo.
echo ==========================================
echo   TESTE DE CONEXÃO COM O SERVIDOR
echo ==========================================
echo.

if not exist venv_dev (
    echo [ERRO] Ambiente virtual nao encontrado. 
    echo Execute primeiro o arquivo SETUP_LOCAL_DEV.bat
    pause
    exit
)

call venv_dev\Scripts\activate
python check_remote_db.py

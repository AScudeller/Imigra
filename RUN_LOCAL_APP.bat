@echo off
pushd "%~dp0"
chcp 65001 > nul
echo ===================================================
echo  INICIANDO SISTEMAS NO SERVIDOR DE DESENVOLVIMENTO
echo ===================================================

echo [1/2] Iniciando Django (Python)...
:: Usa o python do ambiente virtual diretamente
start "Django Server (ERP)" cmd /k "venv_dev\Scripts\python.exe manage.py runserver 0.0.0.0:8000"
echo Django iniciado em http://localhost:8000

echo.
echo [2/2] Iniciando PHP Server (IAMoveis)...
start "PHP Server (IAMoveis)" cmd /k "php -S 0.0.0.0:8090 -t ../iamoveis"
echo PHP iniciado em http://localhost:8090

echo.
echo Servidores rodando!
echo Pressione qualquer tecla para parar e limpar...
pause > nul
exit

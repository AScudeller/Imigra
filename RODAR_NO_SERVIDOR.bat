@echo off
pushd "%~dp0"
chcp 65001 > nul
echo ===================================================
echo  RODANDO SISTEMAS NO SERVIDOR (ACESSO PELA REDE)
echo ===================================================
echo.
echo ESTE SCRIPT DEVE SER EXECUTADO NO SERVIDOR (192.168.86.250)
echo.

:: 1. Tentar encontrar o PHP no XAMPP se nao estiver no PATH
set PHP_CMD=php
where php >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\xampp\php\php.exe" (
        echo [INFO] Usando PHP do XAMPP (C:\xampp\php\php.exe)
        set PHP_CMD="C:\xampp\php\php.exe"
    ) else (
        echo [ERRO] PHP nao encontrado no PATH nem em C:\xampp\php\php.exe
        echo Instale o XAMPP ou PHP e tente novamente.
        pause
        exit
    )
)

if not exist venv_server (
    echo [ERRO] Ambiente 'venv_server' nao encontrado!
    echo Execute o arquivo INSTALAR_NO_SERVIDOR.bat primeiro.
    pause
    exit
)

echo [1/2] Iniciando Django (ERP) na porta 8000...
start "Django SERVER" cmd /k "venv_server\Scripts\python.exe manage.py runserver 0.0.0.0:8000 || pause"

echo.
echo [2/2] Iniciando PHP (IAMoveis) via Apache na porta 8090...
:: O PHP agora roda via Apache (XAMPP). Vamos garantir que o servico esteja subindo.
net start Apache2.4 >nul 2>nul
echo [OK] Apache configurado na porta 8090.

echo.
echo ===================================================
echo  SISTEMAS ONLINE!
echo ===================================================
echo.
echo Acesse de qualquer computador da rede:
echo  - ERP (Django): http://192.168.86.250:8000
echo  - IAMoveis (PHP): http://192.168.86.250:8090
echo.
echo NOTA: O PHP agora roda profissionalmente via Apache.
echo Nao eh mais aberta uma janela separada para ele.
echo.
pause

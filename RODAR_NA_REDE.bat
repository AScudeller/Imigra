@echo off
title ERP Imigracao - Servidor de Rede
color 0A
cls

echo ============================================================
echo   ERP IMIGRACAO - INICIANDO SERVIDOR PARA ACESSO EM REDE
echo ============================================================
echo.

:: Detecta IP automaticamente
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr "192.168"') do (
    set IP=%%a
)
set IP=%IP: =%

echo [INFO] IP desta maquina: %IP%
echo.
echo [INFO] Outros dispositivos devem acessar:
echo.
echo   http://%IP%:8080
echo.
echo ============================================================
echo   DEIXE ESTA JANELA ABERTA ENQUANTO USAR O SISTEMA
echo ============================================================
echo.

:: Ativa o ambiente virtual
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "venv_server\Scripts\activate.bat" (
    call venv_server\Scripts\activate.bat
)

echo [INFO] Iniciando Django na rede (0.0.0.0:8080)...
echo.

python manage.py runserver 0.0.0.0:8080

pause

@echo off
echo ===================================================
echo  RODANDO DIAGNOSTICO DE LOGIN DJANGO
echo ===================================================
echo.
echo Este script vai:
echo 1. Limpar todas as sessoes do banco (fix para "Session data corrupted")
echo 2. Listar usuarios admin existentes
echo 3. Testar a senha manualmente
echo.

cd /d "%~dp0"

if exist venv_server\Scripts\python.exe (
    venv_server\Scripts\python.exe debug_django_login.py
) else (
    echo [ERRO] venv_server nao encontrado.
    python debug_django_login.py
)

echo.
echo DIAGNOSTICO CONCLUIDO.
echo Tire um print desta tela se houver erro.
pause

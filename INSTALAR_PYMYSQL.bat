@echo off
echo ===================================================
echo  INSTALANDO DEPENDENCIAS RESTANTES (PYMYSQL)
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/3] Atualizando PIP...
venv_server\Scripts\python.exe -m pip install --upgrade pip

echo [2/3] Instalando PyMySQL (Driver do Banco)...
venv_server\Scripts\pip install pymysql cryptography

echo [3/3] Instalando outras possiveis faltas...
venv_server\Scripts\pip install django-simple-history reportlab

echo.
echo INSTALACAO CONCLUIDA.
echo Agora execute RODAR_DEBUG_LOGIN.bat novamente ou inicie o servidor.
pause

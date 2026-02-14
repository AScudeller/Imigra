@echo off
chcp 65001 > nul
echo ===================================================
echo  PREPARACAO DO SERVIDOR (Executar APENAS NO SERVIDOR)
echo ===================================================
echo.
echo ATENCAO: Este script deve ser rodado na maquina 192.168.86.250
echo para instalar as dependencias LOCAIS dela.
echo.

if not exist python --version (
    echo [Check] Python verificado.
)

echo [1/3] Criando ambiente virtual do Servidor (venv_server)...
python -m venv venv_server

echo.
echo [2/3] Instalando dependencias no Servidor...
venv_server\Scripts\pip install -r requirements.txt

echo.
echo [3/3] Aplicando migracoes no banco local...
venv_server\Scripts\python manage.py migrate

echo.
echo ===================================================
echo  SERVIDOR PRONTO!
echo ===================================================
echo Agora voce pode usar o arquivo RODAR_NO_SERVIDOR.bat
pause

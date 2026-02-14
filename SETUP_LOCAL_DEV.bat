@echo off
pushd "%~dp0"
chcp 65001 > nul
echo ===================================================
echo  CONFIGURACAO DE AMBIENTE DE DESENVOLVIMENTO LOCAL
echo ===================================================
echo.

if exist venv_dev (
    echo [INFO] Limpando instalação anterior para corrigir caminhos...
    rmdir /s /q venv_dev
)

echo [1/4] Criando ambiente virtual Python (venv_dev)...
python -m venv venv_dev
if errorlevel 1 (
    echo ERRO: Python nao encontrado ou erro ao criar venv.
    echo Verifique se o Python esta instalado e no PATH.
    pause
    exit /b
)

echo.
echo [2/4] Instalando dependencias...
:: Usamos o python diretamente para evitar erro de caminho de rede (UNC)
set PYTHON_ENV=venv_dev\Scripts\python.exe

"%PYTHON_ENV%" -m pip install --upgrade pip
"%PYTHON_ENV%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b
)

echo.
echo [3/4] Configurando Banco de Dados...
echo Tentando rodar migracoes para criar tabelas se nao existirem...
"%PYTHON_ENV%" manage.py migrate

echo.
echo [4/4] Verificando PHP...
php --version > nul 2>&1
if errorlevel 1 (
    echo AVISO: PHP nao encontrado no PATH. O sistema IAMoveis nao rodara.
    echo Instale o PHP ou adicione ao PATH.
) else (
    echo PHP encontrado!
)

echo.
echo ===================================================
echo  AMBIENTE CONFIGURADO COM SUCESSO!
echo ===================================================
echo.
echo Para iniciar os servidores, execute: RUN_LOCAL_APP.bat
pause

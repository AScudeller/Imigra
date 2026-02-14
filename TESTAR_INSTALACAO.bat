@echo off
chcp 65001 >nul
echo ==========================================
echo   TESTE DE INSTALACAO - ERP IMIGRACAO
echo ==========================================
echo.
echo Este script vai preparar o ambiente e testar se tudo esta funcionando.
echo.

:: 1. Verificando Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
   echo    [ERRO FATAL] Python nao encontrado!
   echo    Instale o Python 3.10+ e marque "Add Python to PATH" na instalacao.
   pause
   exit /b
)
echo    [OK] Python encontrado.

:: 2. Checks do MySQL
echo.
echo [2/5] Verificando Banco de Dados...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I /N "mysqld.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo    [OK] XAMPP/MySQL parece estar rodando.
) else (
    echo    [ALERTA] O MySQL nao parece estar rodando.
    echo    Se o teste falhar, abra o XAMPP e inicie o MySQL.
)

:: 3. Ambiente Virtual
echo.
echo [3/5] Configurando Ambiente Virtual...
if not exist venv (
    echo    - Criando pasta 'venv'...
    python -m venv venv
)
echo    - Ativando ambiente...
call venv\Scripts\activate

:: 4. Dependências
echo.
echo [4/5] Instalando bibliotecas (pode demorar)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
   echo.
   echo    [ERRO] Falha ao instalar dependencias no PIP.
   echo    Dica: Se o erro for no 'mysqlclient', voce precisa instalar o "C++ Build Tools" ou baixar o arquivo .whl manualmente.
   pause
   exit /b
)

:: 5. Teste Final
echo.
echo [5/5] Iniciando o Servidor...
echo.
echo    Se tudo der certo, voce vera uma mensagem abaixo dizendo:
echo    "Starting development server at http://0.0.0.0:8000/"
echo.
echo    >>> ABRA SEU NAVEGADOR E ACESSE: http://localhost:8000
echo.
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

pause
pause
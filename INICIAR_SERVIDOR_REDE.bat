@echo off
title ERP Imigracao - Configuracao e Inicio do Servidor
color 0A
cls

:: ============================================================
:: CAMINHO FIXO DO PROJETO - Altere se necessario
:: ============================================================
set PROJETO=C:\Sistemas\ERP_imigracao
set PORTA=8081

echo ============================================================
echo   ERP IMIGRACAO - INICIANDO SERVIDOR
echo   Pasta: %PROJETO%
echo   Porta: %PORTA%
echo ============================================================
echo.

:: Verifica se esta rodando como Administrador
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    color 0C
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR!
    echo.
    echo  1. Feche esta janela
    echo  2. Clique com botao direito neste arquivo .bat
    echo  3. Escolha "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Rodando como Administrador
echo.

:: =============================================================
:: PASSO 1 - Configurar perfil de rede como Privado
:: =============================================================
echo [1/6] Configurando perfil de rede como Privado...
powershell -Command "Get-NetConnectionProfile | Where-Object {$_.NetworkCategory -eq 'Public'} | Set-NetConnectionProfile -NetworkCategory Private" >nul 2>&1
echo [OK] Perfil de rede configurado!
echo.

:: =============================================================
:: PASSO 2 - Liberar porta no Firewall
:: =============================================================
echo [2/6] Liberando porta %PORTA% no Firewall...
netsh advfirewall firewall delete rule name="ERP Imigracao Porta %PORTA%" >nul 2>&1
netsh advfirewall firewall add rule name="ERP Imigracao Porta %PORTA%" dir=in action=allow protocol=TCP localport=%PORTA% >nul 2>&1
echo [OK] Porta %PORTA% liberada!
echo.

:: =============================================================
:: PASSO 3 - Encerrar processo que ja usa a porta (se houver)
:: =============================================================
echo [3/6] Verificando se a porta %PORTA% esta livre...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORTA% " ^| findstr "LISTENING"') do (
    echo [INFO] Encontrado processo usando porta %PORTA% - PID: %%a - Encerrando...
    taskkill /PID %%a /F >nul 2>&1
)
echo [OK] Porta %PORTA% liberada!
echo.

:: =============================================================
:: PASSO 4 - Verificar pasta do projeto
:: =============================================================
echo [4/6] Verificando pasta do projeto...
if not exist "%PROJETO%\manage.py" (
    color 0C
    echo [ERRO] Pasta do projeto nao encontrada: %PROJETO%
    echo        Verifique o caminho na variavel PROJETO no inicio do script.
    echo.
    pause
    exit /b 1
)
echo [OK] Projeto encontrado em: %PROJETO%
cd /d "%PROJETO%"
echo.

:: =============================================================
:: PASSO 5 - Ativar ambiente virtual e instalar dependencias
:: =============================================================
echo [5/6] Configurando ambiente Python...

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] Ambiente virtual .venv ativado
) else if exist "venv_server\Scripts\activate.bat" (
    call venv_server\Scripts\activate.bat
    echo [OK] Ambiente virtual venv_server ativado
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] Ambiente virtual venv ativado
) else (
    echo [AVISO] Ambiente virtual nao encontrado, usando Python do sistema
)

python -c "import django" >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt >nul 2>&1
    pip install -r requirements.txt
    echo.
)
echo [OK] Django pronto!
echo.

:: =============================================================
:: PASSO 6 - Detectar IP e Iniciar
:: =============================================================
echo [6/6] Iniciando sistema ERP Imigracao...

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr "192.168"') do (
    set SERVER_IP=%%a
)
set SERVER_IP=%SERVER_IP: =%
if "%SERVER_IP%"=="" set SERVER_IP=192.168.86.250

echo.
echo ============================================================
echo.
echo   SISTEMA ERP IMIGRACAO DISPONIVEL NA REDE:
echo.
echo     http://%SERVER_IP%:%PORTA%
echo.
echo   Acesse este endereco em:
echo     - Qualquer PC na rede
echo     - Tablet (Wi-Fi na mesma rede)
echo     - Celular (Wi-Fi na mesma rede)
echo.
echo ============================================================
echo   DEIXE ESTA JANELA ABERTA ENQUANTO USAR O SISTEMA
echo ============================================================
echo.

python manage.py runserver 0.0.0.0:%PORTA%

echo.
echo [INFO] Servidor encerrado.
pause

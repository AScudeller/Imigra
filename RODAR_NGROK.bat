@echo off
pushd "%~dp0"
chcp 65001 > nul
echo ===================================================
echo  NGROK - ACESSO EXTERNO (SEM DOMINIO)
echo ===================================================
echo.
echo ESTE SCRIPT DEVE SER RODADO NO SERVIDOR (192.168.86.250).
echo.

if not exist ngrok.exe (
    echo [1/3] O ngrok.exe nao foi encontrado nesta pasta.
    echo.
    echo Passo a passo:
    echo 1. Acesse: https://ngrok.com/download
    echo 2. Baixe a versao para Windows.
    echo 3. Coloque o arquivo "ngrok.exe" aqui junto com este script.
    echo 4. Crie uma conta no site e pegue seu "Authtoken".
    echo.
    pause
    exit
)

echo [2/3] Configurando Autenticacao (Se ja fez, pode pular)...
set /p TOKEN="Cole seu Authtoken aqui (ou pressione ENTER se ja configurou): "
if not "%TOKEN%"=="" (
    ngrok config add-authtoken %TOKEN%
)

:MENU
cls
echo ===================================================
echo  ESCOLHA O SISTEMA PARA COLOCAR NA INTERNET
echo ===================================================
echo.
echo [1] ERP Imigracao (Django - Porta 8000)
echo [2] IAMoveis (PHP - Porta 8090)
echo.
set /p OPCAO="Digite o numero: "

if "%OPCAO%"=="1" (
    echo.
    echo Gerando link para o ERP...
    echo (Copie o link que aparece em "Forwarding")
    echo.
    ngrok http 8000
) else if "%OPCAO%"=="2" (
    echo.
    echo Gerando link para o IAMoveis...
    echo (Copie o link que aparece em "Forwarding")
    echo.
    ngrok http 8090
) else (
    echo Opcao invalida.
    goto MENU
)

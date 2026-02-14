@echo off
pushd "%~dp0"
chcp 65001 > nul
echo ============================================================
echo  CONFIGURANDO ACESSO REMOTO AO MYSQL (EXECUTAR NO SERVIDOR)
echo ============================================================
echo.
echo Este script deve ser executado NA MAQUINA SERVIDOR (192.168.86.250).
echo Ele vai liberar o acesso para que voce possa conectar do seu notebook.
echo.
echo Procurando MySQL no XAMPP...

if exist "C:\xampp\mysql\bin\mysql.exe" (
    set MYSQL_CMD="C:\xampp\mysql\bin\mysql.exe"
) else (
    echo ERRO: MySQL nao encontrado em C:\xampp\mysql\bin.
    echo Verifique onde o XAMPP foi instalado.
    set /p MYSQL_CMD="Digite o caminho completo do mysql.exe: "
)

echo.
echo Executando comandos de permissao...
%MYSQL_CMD% -u root < configurar_mysql_remoto.sql

if errorlevel 0 (
    echo.
    echo SUCESSO! O MySQL agora aceita conexoes de fora.
    echo IMPORTANTE: Verifique se o FIREWALL DO WINDOWS nao esta bloqueando a porta 3306.
) else (
    echo.
    echo FALHA ao configurar permissoes. Verifique as mensagens acima.
)

echo.
pause

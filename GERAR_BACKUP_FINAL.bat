@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

:: ==========================================
:: CONFIGURAÇÃO DE DIRETÓRIOS
:: ==========================================
set "SOURCE_ERP=c:\Users\ascud\OneDrive\Sistemas\ERP_imigracao"
set "SOURCE_IAMOVEIS=c:\Users\ascud\OneDrive\Sistemas\IAMoveisCalculos_V3"
set "DEST_DIR=c:\Users\ascud\OneDrive\MIGRATION_PACKAGE"
set "ZIP_FILE=c:\Users\ascud\OneDrive\MIGRATION_PACKAGE.zip"

echo ========================================================
echo   GERADOR DE PACOTE DE MIGRACAO v3.0 (FINAL)
echo ========================================================
echo.

:: 1. CHECK MYSQL (CRÍTICO)
echo [1/5] Verificando se o Banco de Dados esta ligado...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I /N "mysqld.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo    [OK] MySQL esta RODANDO.
) else (
    echo.
    echo    #########################################################
    echo    [ERRO FATAL] O MYSQL (XAMPP) ESTA DESLIGADO!
    echo    #########################################################
    echo    Sem o banco ligado, os arquivos de backup ficarao VAZIOS.
    echo.
    echo    >> O QUE FAZER AGORA:
    echo    1. Abra o XAMPP Control Panel.
    echo    2. Clique no botao [Start] ao lado do MySQL.
    echo    3. Quando ficar VERDE, rode este script novamente.
    echo.
    pause
    exit /b
)

:: 2. PREPARAR PASTA
echo.
echo [2/5] Limpando pasta antiga...
if exist "%DEST_DIR%" rmdir /s /q "%DEST_DIR%"
mkdir "%DEST_DIR%"

:: 3. EXPORTAR BANCOS
echo.
echo [3/5] Exportando Bancos de Dados...

set MYSQLDUMP_CMD=""
:: Tenta encontrar mysqldump
if exist "D:\xampp\mysql\bin\mysqldump.exe" set MYSQLDUMP_CMD="D:\xampp\mysql\bin\mysqldump.exe"
if exist "C:\xampp\mysql\bin\mysqldump.exe" set MYSQLDUMP_CMD="C:\xampp\mysql\bin\mysqldump.exe"
if %MYSQLDUMP_CMD% == "" set MYSQLDUMP_CMD=mysqldump

echo    - Exportando erp_imigracao...
%MYSQLDUMP_CMD% -u root --databases erp_imigracao --add-drop-database --triggers --routines --events > "%DEST_DIR%\backup_erp_imigracao.sql"
if %errorlevel% neq 0 (
    echo    [ERRO] Falha ao exportar erp_imigracao.
) else (
    echo    [OK] Sucesso.
)

echo    - Exportando iamoveis_calculos...
%MYSQLDUMP_CMD% -u root --databases iamoveis_calculos --add-drop-database --triggers --routines --events > "%DEST_DIR%\backup_iamoveis_calculos.sql"
if %errorlevel% neq 0 (
    echo    [ERRO] Falha ao exportar iamoveis_calculos.
) else (
    echo    [OK] Sucesso.
)

:: 4. COPIAR ARQUIVOS
echo.
echo [4/5] Copiando arquivos dos sistemas...

echo    - ERP Python...
robocopy "%SOURCE_ERP%" "%DEST_DIR%\ERP_imigracao" /E /XD venv .git __pycache__ .idea .vscode media staticfiles /XF *.pyc *.log /R:1 /W:0 /MT:8 /NFL /NDL >NUL

echo    - IAMoveis PHP...
robocopy "%SOURCE_IAMOVEIS%" "%DEST_DIR%\IAMoveisCalculos_V3" /E /XD .git .vscode node_modules backups /XF *.log /R:1 /W:0 /MT:8 /NFL /NDL >NUL

:: Copiar o Guia
if exist "%SOURCE_ERP%\GUIA_MIGRACAO_FINAL.md" copy "%SOURCE_ERP%\GUIA_MIGRACAO_FINAL.md" "%DEST_DIR%\GUIA_MIGRACAO.txt" >NUL

:: 5. ZIPAR
echo.
echo [5/5] Criando arquivo ZIP final (Isso facilita o transporte)...
if exist "%ZIP_FILE%" del "%ZIP_FILE%"
powershell -command "Compress-Archive -Path '%DEST_DIR%' -DestinationPath '%ZIP_FILE%' -Force"

echo.
echo ========================================================
echo   MIGRACAO PRONTA!
echo ========================================================
echo.
echo O arquivo para levar para o novo servidor e:
echo %ZIP_FILE%
echo.
echo 1. Leve esse ZIP para a nova maquina.
echo 2. Extraia e siga o guia que esta dentro dele.
echo.
pause

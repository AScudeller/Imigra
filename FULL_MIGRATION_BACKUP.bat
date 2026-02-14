@echo off
setlocal EnableDelayedExpansion

:: ==========================================
:: CONFIGURAÇÃO DE DIRETÓRIOS
:: ==========================================
:: Ajustando caminhos relativos ou absolutos conhecidos
set "SOURCE_ERP=c:\Users\ascud\OneDrive\Sistemas\ERP_imigracao"
set "SOURCE_IAMOVEIS=c:\Users\ascud\OneDrive\Sistemas\IAMoveisCalculos_V3"
set "DEST_DIR=c:\Users\ascud\OneDrive\MIGRATION_PACKAGE"

:: Database Names
set "DB_ERP=erp_imigracao"
set "DB_IAMOVEIS=iamoveis_calculos"

:: Data Stamp
set TIMESTAMP=%date:~-4%-%date:~3,2%-%date:~0,2%

echo ========================================================
echo PREPARANDO PACOTE DE MIGRACAO
echo ========================================================
echo.

if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"

:: ==========================================
:: 1. LOCALIZAR MYSQLDUMP
:: ==========================================
echo [1/4] Procurando MySQL Dump...
set MYSQLDUMP_CMD=""
if exist "D:\xampp\mysql\bin\mysqldump.exe" set MYSQLDUMP_CMD="D:\xampp\mysql\bin\mysqldump.exe"
if exist "C:\xampp\mysql\bin\mysqldump.exe" set MYSQLDUMP_CMD="C:\xampp\mysql\bin\mysqldump.exe"
:: Tambem tenta no Path
if %MYSQLDUMP_CMD% == "" (
    where mysqldump >nul 2>nul
    if %errorlevel% equ 0 set MYSQLDUMP_CMD=mysqldump
)

if %MYSQLDUMP_CMD% == "" (
    echo ERRO: mysqldump.exe nao encontrado no C: ou D:.
    echo O Backup dos bancos FALHOU. Tente instalar o XAMPP ou rodar onde o MySQL esta.
    pause
    goto FILE_COPY
) else (
    echo Encontrado: %MYSQLDUMP_CMD%
    
    echo.
    echo [2/4] Exportando Banco de Dados...
    
    echo   - Exportando %DB_ERP%...
    %MYSQLDUMP_CMD% -u root --databases %DB_ERP% > "%DEST_DIR%\backup_%DB_ERP%.sql" 2>nul
    if %errorlevel% neq 0 echo     [ALERTA] Falha ao exportar %DB_ERP%. Verifique se o banco existe.
    
    echo   - Exportando %DB_IAMOVEIS%...
    %MYSQLDUMP_CMD% -u root --databases %DB_IAMOVEIS% > "%DEST_DIR%\backup_%DB_IAMOVEIS%.sql" 2>nul
     if %errorlevel% neq 0 echo     [ALERTA] Falha ao exportar %DB_IAMOVEIS%. Verifique se o banco existe.
)

:FILE_COPY
:: ==========================================
:: 3. COPIAR ARQUIVOS
:: ==========================================
echo.
echo [3/4] Copiando arquivos dos sistemas...

echo   - Copiando ERP_imigracao...
robocopy "%SOURCE_ERP%" "%DEST_DIR%\ERP_imigracao" /E /XD venv .git __pycache__ .idea .vscode media staticfiles /XF *.pyc *.log /R:2 /W:1 /MT:8

echo   - Copiando IAMoveisCalculos_V3...
robocopy "%SOURCE_IAMOVEIS%" "%DEST_DIR%\IAMoveisCalculos_V3" /E /XD .git .vscode node_modules backups /XF *.log /R:2 /W:1 /MT:8

:: ==========================================
:: 4. INSTRUCOES FINAIS
:: ==========================================
echo.
echo [4/4] Finalizando...
echo.
echo ========================================================
echo MIGRACAO PRONTA!
echo.
echo 1. A pasta "%DEST_DIR%" contem tudo.
echo 2. Copie essa pasta para o NOVO SERVIDOR.
echo 3. Siga o GUIA_MIGRACAO.md.
echo ========================================================
pause

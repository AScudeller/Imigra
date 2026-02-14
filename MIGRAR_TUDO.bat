@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

:: ==========================================
:: DEFINICAO DE CAMINHOS
:: ==========================================
set "ROOT_PATH=c:\Users\ascud\OneDrive"
set "SOURCE_ERP=%ROOT_PATH%\Sistemas\ERP_imigracao"
set "SOURCE_IAM=%ROOT_PATH%\Sistemas\IAMoveisCalculos_V3"

:: Pasta temporaria para montar o pacote
set "TEMP_DIR=%ROOT_PATH%\Sistemas\TEMP_PACOTE"

:: Arquivo Final
set "FINAL_ZIP=%ROOT_PATH%\Sistemas\ERP_imigracao\PACOTE_MIGRACAO_FINAL.zip"

echo ========================================================
echo   MIGRACAO : SISTEMA DE BACKUP AUTOMATICO
echo ========================================================
echo.

:: 1. VERIFICAR MYSQL (OBRIGATORIO)
echo [1/6] Verificando se o XAMPP/MySQL esta ligado...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I /N "mysqld.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo    [OK] MySQL detectado.
) else (
    echo.
    echo    [ERRO] O MySQL ESTA DESLIGADO!
    echo    Sem ele, nao consigo pegar os dados.
    echo.
    echo    POR FAVOR: Abra o XAMPP e clique em START no MySQL.
    echo.
    pause
    exit /b
)

:: 2. LIMPEZA
echo.
echo [2/6] Limpando arquivos antigos...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
if exist "%FINAL_ZIP%" del "%FINAL_ZIP%"
mkdir "%TEMP_DIR%"

:: 3. EXPORTAR DADOS (SQL)
echo.
echo [3/6] Exportando Banco de Dados...

set MYSQLDUMP=mysqldump
if exist "D:\xampp\mysql\bin\mysqldump.exe" set MYSQLDUMP="D:\xampp\mysql\bin\mysqldump.exe"
if exist "C:\xampp\mysql\bin\mysqldump.exe" set MYSQLDUMP="C:\xampp\mysql\bin\mysqldump.exe"

echo    - Salvando ERP Imigracao...
%MYSQLDUMP% -u root --databases erp_imigracao --add-drop-database --routines > "%TEMP_DIR%\banco_erp_imigracao.sql"

echo    - Salvando IAMoveis...
%MYSQLDUMP% -u root --databases iamoveis_calculos --add-drop-database --routines > "%TEMP_DIR%\banco_iamoveis.sql"

if not exist "%TEMP_DIR%\banco_erp_imigracao.sql" (
    echo    [ERRO CRITICO] O arquivo SQL nao foi criado. Verifique o XAMPP.
    pause
    exit /b
)

:: 4. COPIAR SISTEMAS
echo.
echo [4/6] Copiando arquivos dos sistemas (Isso pode demorar)...

:: Copia ERP
mkdir "%TEMP_DIR%\ERP_imigracao"
robocopy "%SOURCE_ERP%" "%TEMP_DIR%\ERP_imigracao" /E /XD venv .git __pycache__ .idea .vscode media staticfiles /XF *.pyc *.log /R:0 /W:0 /MT:8 /NFL /NDL >NUL
echo    - ERP copiado.

:: Copia IAMoveis
mkdir "%TEMP_DIR%\iamoveis"
robocopy "%SOURCE_IAM%" "%TEMP_DIR%\iamoveis" /E /XD .git .vscode node_modules backups /XF *.log /R:0 /W:0 /MT:8 /NFL /NDL >NUL
echo    - IAMoveis copiado.

:: Copia as instrucoes
copy "%SOURCE_ERP%\COMO_INSTALAR.txt" "%TEMP_DIR%\LEIA_ME_PRIMEIRO.txt" >NUL

:: 5. CRIAR ZIP
echo.
echo [5/6] Criando o arquivo ZIP final...
powershell -command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%FINAL_ZIP%' -Force"

:: 6. LIMPEZA FINAL
rmdir /s /q "%TEMP_DIR%"

echo.
echo ========================================================
echo   SUCESSO! TUDO PRONTO.
echo ========================================================
echo.
echo O arquivo que voce deve levar para a nova maquina e:
echo.
echo    PACOTE_MIGRACAO_FINAL.zip
echo.
echo (Ele esta nesta mesma pasta onde voce rodou o script)
echo.
pause

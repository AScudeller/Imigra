@echo off
echo ===================================================
echo  CORRIGINDO FIREWALL DO SERVIDOR (PORTA 8000)
echo ===================================================
echo.
echo Precisa ser executado como ADMINISTRADOR.
echo.

netsh advfirewall firewall delete rule name="Acesso ERP Python (8000)" >nul
netsh advfirewall firewall add rule name="Acesso ERP Python (8000)" dir=in action=allow protocol=TCP localport=8000

echo Regra recriada com sucesso.
echo.
echo Verificando portas ouvindo...
netstat -an | findstr 8000
echo.
echo Se nada apareceu acima, o Django NAO esta rodando.
echo Execute RODAR_NO_SERVIDOR.bat
echo.
pause

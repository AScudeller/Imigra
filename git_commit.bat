@echo off
echo ============================================
echo  ERP IMIGRACAO - Git Commit
echo ============================================
echo.

cd /d C:\Sistemas\ERP_imigracao

echo [1/3] Status atual...
git status
echo.

echo [2/3] Adicionando arquivos...
git add -A
echo.

echo [3/3] Realizando commit...
git commit -m "fix: corrigir conexao com MariaDB no servidor

- Alterar HOST do banco de '127.0.0.1' para 'localhost'
- Resolver erro: Host 'Server' is not allowed to connect to this MariaDB server
- Sistema ERP_imigracao (G IMIGRA) funcionando em http://192.168.86.250:8081"

echo.
echo [OK] Commit realizado!
echo.
git log --oneline -5
echo.
pause

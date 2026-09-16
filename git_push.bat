@echo off
echo ============================================
echo  ERP IMIGRACAO - Git Push (GitHub)
echo ============================================
echo.
cd /d C:\Sistemas\ERP_imigracao
git status
echo.
echo Enviando commits para o GitHub...
git push origin main
echo.
pause
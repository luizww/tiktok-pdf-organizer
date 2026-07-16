@echo off
setlocal

echo Instalando dependencias...
py -m pip install -r requirements-dev.txt
if errorlevel 1 goto :error

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Gerando executavel...
py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name TikTokPDFOrganizer ^
  --collect-all customtkinter ^
  main.py
if errorlevel 1 goto :error

echo.
echo =============================================
echo Executavel criado em dist\TikTokPDFOrganizer
echo =============================================
pause
exit /b 0

:error
echo.
echo Nao foi possivel gerar o executavel.
pause
exit /b 1

@echo off
setlocal
pushd "%~dp0"

echo Instalando dependencias...
py -m pip install -r requirements-dev.txt
if errorlevel 1 goto :error

echo Executando testes...
py -m unittest discover -s tests -v
if errorlevel 1 goto :error

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Gerando executavel independente...
py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --noupx ^
  --name TikTokPDFOrganizer ^
  --collect-all customtkinter ^
  --collect-all pymupdf ^
  --hidden-import fitz ^
  main.py
if errorlevel 1 goto :error

if not exist "dist\TikTokPDFOrganizer.exe" goto :error

echo.
echo ======================================================
echo Executavel criado em dist\TikTokPDFOrganizer.exe
echo ======================================================
popd
pause
exit /b 0

:error
echo.
echo Nao foi possivel testar ou gerar o executavel.
popd
pause
exit /b 1

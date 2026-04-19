@echo off
title Установка RuIAN
echo ========================================
echo    Установка RuIAN - твоей нейросети
echo ========================================
echo.

:: Создаём папку
mkdir "%USERPROFILE%\RuIAN" 2>nul
cd "%USERPROFILE%\RuIAN"

:: Скачиваем файлы
echo Скачивание RuIAN...
curl -L -o ruian_server.py https://raw.githubusercontent.com/qoxfdcyd2654/ruian/main/ruian_server.py

:: Устанавливаем Python если нет
python --version >nul 2>&1
if errorlevel 1 (
    echo Установка Python...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
)

:: Запуск
echo.
echo ========================================
echo    RuIAN установлен!
echo    Запусти ruian_server.py в папке
echo    %USERPROFILE%\RuIAN
echo ========================================
start python ruian_server.py
start https://qoxfdcyd2654.github.io/ruian
pause

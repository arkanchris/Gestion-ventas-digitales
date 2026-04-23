@echo off
title StreamControl
cd /d "C:\Users\Acer\Desktop\StreamControl"

:: Intentar ejecutar el .exe compilado primero
if exist "C:\Users\Acer\Desktop\StreamControl\dist\StreamControl.exe" (
    start "" "C:\Users\Acer\Desktop\StreamControl\dist\StreamControl.exe"
    exit
)

:: Si no hay exe, usar Python directamente
python main.py

if errorlevel 1 (
    echo.
    echo ERROR. Asegurate de tener Python instalado.
    pause
)

@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Proyecto Integrador 3 - Santiago Arango
echo === Proyecto Integrador 3 - Santiago Arango ===
where python >nul 2>nul || (echo No se encontro Python. Instalalo desde python.org y vuelve a intentar. & pause & exit /b 1)
if not exist .venv (
  echo Creando ambiente virtual...
  python -m venv .venv || (pause & exit /b 1)
)
call .venv\Scripts\activate.bat
echo Instalando librerias...
python -m pip install --quiet --disable-pip-version-check -r requirements.txt || (echo Error instalando librerias. & pause & exit /b 1)
set MPLBACKEND=Agg
echo Ejecutando el analisis...
python analisis_desercion.py > salida_analisis.txt 2>&1
if errorlevel 1 (echo El script fallo. Revisa salida_analisis.txt & type salida_analisis.txt & pause & exit /b 1)
echo Listo. Graficos y decisiones.csv regenerados en Data\processed
echo La salida completa quedo en salida_analisis.txt
start "" informe.html
pause

@echo off
cd /d "%~dp0"
echo Iniciando Dashboard de Ventas Luctron...
echo Se abrira en http://localhost:8766
echo Para cerrar, cerra esta ventana.
python servidor_dashboard.py
pause

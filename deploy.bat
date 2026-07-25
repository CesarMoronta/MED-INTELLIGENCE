@echo off
title Desplegar MED-INTELLIGENCE a Google Cloud
echo ==========================================================
echo   Desplegando MED-INTELLIGENCE a Google Cloud Run...
echo ==========================================================
echo.

:: Cambiar al directorio del proyecto
cd /d "c:\Users\cmoro\OneDrive\Documents\GitHub\MED-INTELLIGENCE"

:: Ejecutar el comando de Google Cloud
call gcloud builds submit --config=cloudbuild.yaml

echo.
echo ==========================================================
echo   Proceso finalizado. Puedes cerrar esta ventana.
echo ==========================================================
pause

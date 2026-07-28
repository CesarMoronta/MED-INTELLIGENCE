@echo off
setlocal enabledelayedexpansion
title Desplegar MED-INTELLIGENCE a Google Cloud

echo ==========================================================
echo   Desplegando MED-INTELLIGENCE a Google Cloud Run...
echo ==========================================================
echo.

:: Cambiar dinamicamente al directorio donde se encuentra este script
cd /d "%~dp0"

:: Verificar que cloudbuild.yaml exista en este directorio
if not exist "%~dp0cloudbuild.yaml" (
    echo [ERROR] No se encontro el archivo cloudbuild.yaml en:
    echo %~dp0
    echo.
    echo Asegurate de ejecutar deploy.bat dentro de la carpeta raiz del proyecto.
    echo.
    pause
    exit /b 1
)

:: Verificar si gcloud esta instalado y disponible en el PATH
where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] El comando 'gcloud' no esta instalado o no se encuentra en el PATH.
    echo Por favor instala Google Cloud SDK o agregalo a las variables de entorno de este equipo.
    echo.
    pause
    exit /b 1
)

echo Directorio del proyecto: %CD%
echo Iniciando envio a Google Cloud Build...
echo.

:: Ejecutar la construccion y despliegue en Cloud Run
call gcloud builds submit --config=cloudbuild.yaml

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ocurrio un error durante el despliegue a Google Cloud.
    echo Revisa el registro de la consola anterior.
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo ==========================================================
echo   ¡Despliegue completado con éxito!
echo ==========================================================
echo.
pause

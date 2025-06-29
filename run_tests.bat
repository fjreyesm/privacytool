@echo off
REM Script de inicio rápido para pruebas en Windows 11
REM Ejecuta los scripts de pruebas de PrivacyTool

echo =====================================
echo   PRIVACYTOOL - SCRIPT DE PRUEBAS
echo =====================================
echo.

REM Verificar que Docker está corriendo
echo [1/5] Verificando Docker...
docker compose ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker no está corriendo o no hay containers activos
    echo Ejecuta: docker compose up -d
    pause
    exit /b 1
)
echo ✅ Docker está funcionando

REM Verificar que los containers están corriendo
echo.
echo [2/5] Verificando containers...
docker compose exec web python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Container web no responde
    echo Ejecuta: docker compose restart
    pause
    exit /b 1
)
echo ✅ Container web está activo

REM Mostrar menú de opciones
echo.
echo [3/5] Selecciona el tipo de prueba:
echo.
echo   1. Pruebas rápidas (5 min)
echo   2. Pruebas completas (15 min)
echo   3. Solo análisis de regresión
echo   4. Solo pruebas de seguridad
echo   5. Solo cobertura de código
echo   6. Ejecutar pruebas originales de Django
echo.
set /p choice="Selecciona una opción (1-6): "

echo.
echo [4/5] Ejecutando pruebas seleccionadas...

if "%choice%"=="1" (
    echo 🏃‍♂️ Ejecutando pruebas rápidas...
    docker compose exec web python test_runner_privacytool.py quick
) else if "%choice%"=="2" (
    echo 🔍 Ejecutando suite completa de pruebas...
    docker compose exec web python test_runner_privacytool.py
) else if "%choice%"=="3" (
    echo 🔄 Ejecutando análisis de regresión...
    docker compose exec web python regression_test_analyzer.py
) else if "%choice%"=="4" (
    echo 🔒 Ejecutando pruebas de seguridad...
    docker compose exec web python test_runner_privacytool.py security
) else if "%choice%"=="5" (
    echo 📊 Ejecutando análisis de cobertura...
    docker compose exec web python test_runner_privacytool.py coverage
) else if "%choice%"=="6" (
    echo 🧪 Ejecutando pruebas originales de Django...
    docker compose exec web python manage.py test --verbosity=2
) else (
    echo ❌ Opción no válida. Ejecutando pruebas por defecto...
    docker compose exec web python manage.py test
)

echo.
echo [5/5] ✅ Pruebas completadas!
echo.

REM Mostrar información adicional
echo 💡 COMANDOS ÚTILES:
echo.
echo   - Ver logs:           docker compose logs web
echo   - Reiniciar:          docker compose restart
echo   - Shell Django:       docker compose exec web python manage.py shell
echo   - Verificar seguridad: docker compose exec web python manage.py check --deploy
echo.

REM Preguntar si quiere ver reportes
set /p viewreports="¿Quieres ver los reportes generados? (s/n): "
if /i "%viewreports%"=="s" (
    echo.
    echo 📋 Buscando reportes generados...
    dir test_report_*.json 2>nul
    dir regression_analysis_*.json 2>nul
    echo.
    echo Los reportes están en formato JSON para análisis detallado.
)

echo.
echo ¡Gracias por usar PrivacyTool Testing Suite! 🚀
pause

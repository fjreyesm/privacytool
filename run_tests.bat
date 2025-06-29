@echo off
REM Script de inicio rápido para pruebas en Windows 11 - VERSIÓN CORREGIDA
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
echo   1. Pruebas rápidas (Django tests)
echo   2. Pruebas completas (Django tests + check)
echo   3. Análisis de seguridad
echo   4. Solo pruebas de newsletter
echo   5. Solo pruebas de core
echo   6. Ver estado de migraciones
echo.
set /p choice="Selecciona una opción (1-6): "

echo.
echo [4/5] Ejecutando pruebas seleccionadas...

if "%choice%"=="1" (
    echo 🏃‍♂️ Ejecutando pruebas rápidas de Django...
    docker compose exec web python manage.py test --verbosity=2
) else if "%choice%"=="2" (
    echo 🔍 Ejecutando suite completa...
    docker compose exec web python manage.py test --verbosity=2
    echo.
    echo 🔒 Verificando configuración de seguridad...
    docker compose exec web python manage.py check --deploy
) else if "%choice%"=="3" (
    echo 🔒 Ejecutando verificaciones de seguridad...
    docker compose exec web python manage.py check --deploy
    echo.
    echo 🔍 Verificando configuración del proyecto...
    docker compose exec web python manage.py check
) else if "%choice%"=="4" (
    echo 📧 Ejecutando pruebas de newsletter...
    docker compose exec web python manage.py test newsletter --verbosity=2
) else if "%choice%"=="5" (
    echo 🧪 Ejecutando pruebas de core...
    docker compose exec web python manage.py test core --verbosity=2
) else if "%choice%"=="6" (
    echo 🔄 Verificando estado de migraciones...
    docker compose exec web python manage.py showmigrations
    echo.
    echo 🔍 Verificando problemas de migraciones...
    docker compose exec web python manage.py check
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
echo   - Ver migraciones:    docker compose exec web python manage.py showmigrations
echo.

REM Preguntar si quiere ver información del sistema
set /p viewinfo="¿Quieres ver información del sistema? (s/n): "
if /i "%viewinfo%"=="s" (
    echo.
    echo 📋 Información del sistema Django:
    echo.
    echo --- Python version ---
    docker compose exec web python --version
    echo.
    echo --- Django version ---
    docker compose exec web python -c "import django; print('Django:', django.get_version())"
    echo.
    echo --- Apps instaladas ---
    docker compose exec web python manage.py diffsettings --only-changed
    echo.
)

echo.
echo ¡Gracias por usar PrivacyTool Testing Suite! 🚀
echo.
echo 💡 TIP: Para ejecutar los scripts Python avanzados:
echo    docker compose exec web python test_runner_privacytool.py
echo    docker compose exec web python regression_test_analyzer.py
echo.
pause

@echo off
echo ================================================================
echo 🔧 NEWSLETTER EMAIL FIX - PRIVACYTOOL
echo ================================================================
echo.

echo 📋 Paso 1: Copiando configuración de Gmail...
copy ".env.gmail" ".env"
if %ERRORLEVEL% == 0 (
    echo ✅ Archivo .env.gmail copiado a .env exitosamente
) else (
    echo ❌ Error copiando archivo. Verifica que .env.gmail existe
    pause
    exit /b 1
)

echo.
echo ⚠️  IMPORTANTE: Edita el archivo .env y:
echo    1. Reemplaza 'xxxx_tu_app_password_aqui' con tu Google App Password
echo    2. Verifica que el email sea correcto
echo.
echo 📱 Para obtener tu Google App Password:
echo    1. Ve a tu cuenta Google → Seguridad
echo    2. Habilita autenticación de 2 pasos
echo    3. Busca "Contraseñas de aplicaciones"
echo    4. Genera una nueva para "Mail"
echo    5. Copia los 16 caracteres (sin espacios)
echo.

set /p continue="¿Ya configuraste tu App Password en .env? (s/n): "
if /i not "%continue%"=="s" (
    echo.
    echo 📝 Por favor, edita .env primero y luego ejecuta este script de nuevo.
    notepad .env
    pause
    exit /b 0
)

echo.
echo 🐳 Paso 2: Reiniciando contenedores Docker...
docker compose down
docker compose up -d

echo.
echo ⏳ Esperando que los contenedores estén listos...
timeout /t 10

echo.
echo 🔍 Paso 3: Verificando configuración de email...
docker compose exec web python manage.py email_diagnosis --check-config

echo.
echo 📧 Paso 4: Enviando email de prueba...
set /p test_email="Introduce tu email para la prueba: "
docker compose exec web python manage.py email_diagnosis --email %test_email%

echo.
echo 🧪 Paso 5: Probando el newsletter real...
echo Ahora ve a tu navegador y:
echo 1. Abre http://127.0.0.1:8000
echo 2. Suscríbete al newsletter con un email de prueba
echo 3. Deberías recibir el email de confirmación
echo.

echo 📊 Paso 6: Ver logs en tiempo real (opcional)
set /p view_logs="¿Quieres ver los logs en tiempo real? (s/n): "
if /i "%view_logs%"=="s" (
    echo.
    echo 📝 Presiona Ctrl+C para salir de los logs
    docker compose logs -f web
)

echo.
echo ✅ Fix del newsletter completado!
echo.
echo 🔧 Si sigues teniendo problemas:
echo    1. Verifica que el App Password sea correcto
echo    2. Revisa que no tengas caracteres especiales en .env
echo    3. Ejecuta: docker compose exec web python manage.py email_diagnosis --check-config
echo    4. Revisa la carpeta de spam en tu email
echo.
pause
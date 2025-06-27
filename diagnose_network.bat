@echo off
echo ================================================================
echo 🌐 DIAGNÓSTICO DE RED PARA SMTP - PRIVACYTOOL
echo ================================================================
echo.

echo 📋 Paso 1: Verificando conectividad básica de internet...
docker compose exec web ping -c 3 8.8.8.8
if %ERRORLEVEL% neq 0 (
    echo ❌ No hay conectividad a internet desde el contenedor
    echo    Esto es un problema de configuración de Docker Desktop
    goto :network_fix
) else (
    echo ✅ Conectividad a internet OK
)

echo.
echo 📋 Paso 2: Verificando conectividad a Gmail SMTP...
echo Probando conexión a smtp.gmail.com:587...
docker compose exec web timeout 10 bash -c "echo 'quit' | telnet smtp.gmail.com 587"
if %ERRORLEVEL% neq 0 (
    echo ❌ No puede conectar a Gmail SMTP
    echo    Posible problema de firewall o proxy corporativo
    goto :smtp_fix
) else (
    echo ✅ Conectividad a Gmail SMTP OK
)

echo.
echo 📋 Paso 3: Verificando DNS...
docker compose exec web nslookup smtp.gmail.com
if %ERRORLEVEL% neq 0 (
    echo ❌ Problema de resolución DNS
    goto :dns_fix
) else (
    echo ✅ Resolución DNS OK
)

echo.
echo ✅ Todas las verificaciones de red pasaron!
echo 📧 Ahora vamos a probar el email...
docker compose exec web python manage.py email_diagnosis --email test@yoursecurescan.com
goto :end

:network_fix
echo.
echo 🔧 SOLUCIONES PARA PROBLEMAS DE RED:
echo.
echo 1. Reiniciar Docker Desktop:
echo    - Click derecho en el ícono de Docker Desktop
echo    - Seleccionar "Restart"
echo    - Esperar que se reinicie completamente
echo.
echo 2. Verificar configuración de red de Docker:
echo    - Abrir Docker Desktop
echo    - Ir a Settings → Resources → Network
echo    - Asegurarse que esté configurado correctamente
echo.
echo 3. Probar con red del host (temporal):
set /p use_host_network="¿Quieres probar con red del host? (s/n): "
if /i "%use_host_network%"=="s" (
    echo Deteniendo contenedores actuales...
    docker compose down
    echo Iniciando con red del host...
    docker compose -f compose.network-debug.yml up -d
    echo Esperando que los contenedores estén listos...
    timeout /t 15
    echo Probando conectividad...
    docker compose -f compose.network-debug.yml exec web ping -c 3 8.8.8.8
)
goto :end

:smtp_fix
echo.
echo 🔧 SOLUCIONES PARA PROBLEMAS DE SMTP:
echo.
echo 1. Verificar firewall de Windows:
echo    - Buscar "Windows Defender Firewall" en el menú inicio
echo    - Permitir Docker Desktop y sus puertos
echo.
echo 2. Si estás en una red corporativa:
echo    - Pueden estar bloqueando el puerto 587
echo    - Consulta con tu administrador de red
echo.
echo 3. Probar puerto alternativo (puerto 465 con SSL):
echo    Esto requiere cambiar la configuración en .env:
echo    EMAIL_PORT=465
echo    EMAIL_USE_TLS=False
echo    EMAIL_USE_SSL=True
echo.
set /p try_port_465="¿Quieres probar el puerto 465? (s/n): "
if /i "%try_port_465%"=="s" (
    echo Creando configuración con puerto 465...
    copy .env .env.backup
    powershell -Command "(Get-Content .env) -replace 'EMAIL_PORT=587', 'EMAIL_PORT=465' -replace 'EMAIL_USE_TLS=True', 'EMAIL_USE_TLS=False' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'EMAIL_USE_SSL=False', 'EMAIL_USE_SSL=True' | Set-Content .env"
    echo Reiniciando contenedores...
    docker compose restart web
    timeout /t 10
    echo Probando con puerto 465...
    docker compose exec web python manage.py email_diagnosis --email test@yoursecurescan.com
)
goto :end

:dns_fix
echo.
echo 🔧 SOLUCIONES PARA PROBLEMAS DE DNS:
echo.
echo 1. Cambiar DNS de Docker:
echo    - Docker Desktop → Settings → Docker Engine
echo    - Agregar configuración de DNS:
echo      {
echo        "dns": ["8.8.8.8", "1.1.1.1"]
echo      }
echo.
echo 2. Usar IP directa (temporal):
echo    - Buscar IP de smtp.gmail.com
echo    - Usar IP en lugar del hostname
echo.
nslookup smtp.gmail.com
echo.
set /p restart_docker="¿Quieres reiniciar Docker Desktop ahora? (s/n): "
if /i "%restart_docker%"=="s" (
    echo Reiniciando Docker Desktop...
    echo NOTA: Esto puede tomar varios minutos
    taskkill /f /im "Docker Desktop.exe"
    timeout /t 5
    start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
    echo Esperando que Docker Desktop se reinicie...
    timeout /t 60
)
goto :end

:end
echo.
echo 🔍 INFORMACIÓN ADICIONAL:
echo.
echo Si los problemas persisten:
echo 1. Verifica que no tengas proxy corporativo
echo 2. Prueba desde fuera de la red corporativa (hotspot móvil)
echo 3. Contacta a tu administrador de red si estás en empresa
echo 4. Como último recurso, usa un servicio SMTP alternativo
echo.
pause
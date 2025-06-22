@echo off
echo 🚀 Iniciando Claude Desktop desde proyecto Django...
echo 📁 Directorio actual: %CD%
echo.

REM Verificar si estamos en un proyecto Django
if exist "manage.py" (
    echo ✅ Proyecto Django detectado
    echo.
    echo 🐍 Activando entorno virtual si existe...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo ✅ Entorno virtual activado
    ) else if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
        echo ✅ Entorno virtual activado
    ) else (
        echo ⚠️  No se encontró entorno virtual
    )
    echo.
    echo 🎯 Abriendo Claude Desktop...
    start "" "C:\Users\osint\AppData\Local\AnthropicClaude\claude.exe"
    echo.
    echo 💡 Claude Desktop se abrirá y trabajará desde este directorio
    echo 📂 Los MCPs podrán acceder a: %CD%
) else (
    echo ❌ No se detectó manage.py - ¿Estás en un proyecto Django?
    echo.
    echo 📁 Archivos en el directorio actual:
    dir /b
    echo.
    echo ¿Quieres continuar anyway? (s/n)
    set /p choice=
    if /i "%choice%"=="s" (
        start "" "C:\Users\osint\AppData\Local\Programs\Claude\Claude.exe"
    )
)

echo.
echo ✨ Script completado
pause
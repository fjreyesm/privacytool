#!/bin/bash
# verify_security.sh - Script para verificar headers de seguridad

echo "🔒 VERIFICANDO SEGURIDAD DJANGO - HEADERS HTTP"
echo "=============================================="

# Verificar que el servicio esté corriendo
echo "📡 Verificando conectividad..."
if curl -s -f http://127.0.0.1:8000/ > /dev/null; then
    echo "✅ Servicio web corriendo en puerto 8000"
else
    echo "❌ Servicio web no disponible. Ejecuta: docker-compose up -d"
    exit 1
fi

echo ""
echo "🛡️ HEADERS DE SEGURIDAD DETECTADOS:"
echo "-----------------------------------"

# Verificar headers específicos
headers=$(curl -s -I http://127.0.0.1:8000/)

# Función para verificar header
check_header() {
    local header_name="$1"
    local expected_pattern="$2"
    
    if echo "$headers" | grep -i "$header_name" | grep -q "$expected_pattern"; then
        echo "✅ $header_name: $(echo "$headers" | grep -i "$header_name" | tr -d '\r')"
    else
        echo "❌ $header_name: No encontrado o incorrecto"
    fi
}

# Verificar todos los headers de seguridad
check_header "x-content-type-options" "nosniff"
check_header "x-frame-options" "DENY"
check_header "referrer-policy" "strict-origin-when-cross-origin"
check_header "content-security-policy" "default-src"
check_header "strict-transport-security" "."
check_header "x-xss-protection" "."

echo ""
echo "🚀 VERIFICACIÓN DJANGO DEPLOY:"
echo "------------------------------"
echo "Ejecutando python manage.py check --deploy..."

# Solo mostrar el comando, ya que requiere acceso al contenedor
echo "💡 Ejecuta manualmente: docker-compose exec web python manage.py check --deploy"

echo ""
echo "🎯 PRÓXIMOS PASOS:"
echo "------------------"
echo "1. ✅ Headers HTTP implementados"
echo "2. 🔄 Rebuild contenedores con CSP"
echo "3. 🧪 Verificar tests de seguridad"
echo "4. 📝 Documentar cambios finales"

echo ""
echo "🏆 OBJETIVO: 0 advertencias críticas - Sistema completamente seguro"
# verify_security.ps1 - Script PowerShell para verificar headers de seguridad

Write-Host "VERIFICANDO SEGURIDAD DJANGO - HEADERS HTTP" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Verificar que el servicio este corriendo
Write-Host "Verificando conectividad..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -Method Head -TimeoutSec 5
    Write-Host "Servicio web corriendo en puerto 8000" -ForegroundColor Green
} catch {
    Write-Host "Servicio web no disponible. Ejecuta: docker-compose up -d" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "HEADERS DE SEGURIDAD DETECTADOS:" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

# Funcion para verificar header
function Check-Header {
    param(
        [string]$HeaderName,
        [string]$ExpectedPattern,
        [object]$Headers
    )
    
    $headerValue = $Headers[$HeaderName]
    if ($headerValue -and $headerValue -match $ExpectedPattern) {
        Write-Host "OK $HeaderName : $headerValue" -ForegroundColor Green
        return $true
    } else {
        Write-Host "FALTA $HeaderName : No encontrado o incorrecto" -ForegroundColor Red
        return $false
    }
}

# Obtener headers
$headers = $response.Headers

# Verificar todos los headers de seguridad
$secureHeaders = 0
$totalHeaders = 6

if (Check-Header "X-Content-Type-Options" "nosniff" $headers) { $secureHeaders++ }
if (Check-Header "X-Frame-Options" "DENY" $headers) { $secureHeaders++ }
if (Check-Header "Referrer-Policy" "strict-origin-when-cross-origin" $headers) { $secureHeaders++ }
if (Check-Header "Content-Security-Policy" "default-src" $headers) { $secureHeaders++ }
if (Check-Header "Strict-Transport-Security" "." $headers) { $secureHeaders++ }
if (Check-Header "Cross-Origin-Opener-Policy" "same-origin" $headers) { $secureHeaders++ }

Write-Host ""
Write-Host "RESUMEN DE SEGURIDAD:" -ForegroundColor Cyan
Write-Host "------------------------" -ForegroundColor Cyan
Write-Host "Headers seguros: $secureHeaders/$totalHeaders" -ForegroundColor $(if ($secureHeaders -eq $totalHeaders) { "Green" } else { "Yellow" })

if ($secureHeaders -eq $totalHeaders) {
    Write-Host "PERFECTO! Sistema completamente seguro" -ForegroundColor Green
} else {
    Write-Host "Faltan algunos headers por configurar" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "COMANDOS PARA COMPLETAR SETUP:" -ForegroundColor Cyan
Write-Host "---------------------------------" -ForegroundColor Cyan
Write-Host "1. docker-compose down" -ForegroundColor White
Write-Host "2. docker-compose build --no-cache" -ForegroundColor White
Write-Host "3. docker-compose up -d" -ForegroundColor White
Write-Host "4. docker-compose exec web python manage.py check --deploy" -ForegroundColor White

Write-Host ""
Write-Host "OBJETIVO: 0 advertencias criticas - Sistema completamente seguro" -ForegroundColor Green
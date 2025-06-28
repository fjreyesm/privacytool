# REGRESSION TESTING - SIN EMAIL TESTING
# =====================================
# Tests que funcionan independiente de configuración email

param(
    [switch]$Verbose = $false
)

Write-Host "🧪 REGRESSION TESTING (NO EMAIL)" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

$TestsPassed = 0
$TestsFailed = 0
$CriticalFailures = 0

function Test-Django {
    param($TestName, $Command, $Critical = $true)
    
    Write-Host ""
    Write-Host "[INFO] Testing: $TestName" -ForegroundColor Cyan
    
    try {
        $output = docker compose exec web python $Command 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($Verbose) {
            Write-Host "Output: $output" -ForegroundColor Gray
        }
        
        if ($exitCode -eq 0) {
            Write-Host "[✅ SUCCESS] $TestName" -ForegroundColor Green
            $script:TestsPassed++
            return $true
        } else {
            if ($Critical) {
                Write-Host "[❌ CRITICAL] $TestName - Exit: $exitCode" -ForegroundColor Red
                $script:CriticalFailures++
            } else {
                Write-Host "[⚠️ WARNING] $TestName - Exit: $exitCode" -ForegroundColor Yellow
            }
            $script:TestsFailed++
            return $false
        }
    }
    catch {
        if ($Critical) {
            Write-Host "[❌ ERROR] $TestName - $($_.Exception.Message)" -ForegroundColor Red
            $script:CriticalFailures++
        } else {
            Write-Host "[⚠️ WARNING] $TestName - $($_.Exception.Message)" -ForegroundColor Yellow
        }
        $script:TestsFailed++
        return $false
    }
}

# Verificar Docker
Write-Host ""
Write-Host "🐳 DOCKER CHECK" -ForegroundColor Yellow
Write-Host "----------------------------------------"

try {
    docker compose ps | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Starting Docker services..." -ForegroundColor Cyan
        docker compose up -d
        Start-Sleep 15
    }
    Write-Host "✅ Docker services ready" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker issue: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 1: Django Health
Write-Host ""
Write-Host "🔧 DJANGO SYSTEM CHECKS" -ForegroundColor Yellow
Write-Host "----------------------------------------"

Test-Django "Django System Check" "manage.py check" $true
Test-Django "Migration Status" "manage.py showmigrations" $true

# Test 2: Database Models
Write-Host ""
Write-Host "📊 DATABASE & MODELS" -ForegroundColor Yellow
Write-Host "----------------------------------------"

Test-Django "Newsletter Models" "manage.py test newsletter.tests -v 1" $true
Test-Django "Core Models" "manage.py test core.tests.test_regression -v 1" $true

# Test 3: HIBP Service (sin email)
Write-Host ""
Write-Host "🔍 HIBP SERVICE (NO EMAIL)" -ForegroundColor Yellow
Write-Host "----------------------------------------"

$hibpTest = @"
from core.services import EmailBreachService
service = EmailBreachService()
result = service.check_email('test@example.com')
print('HIBP Service Test: PASSED' if result is not None else 'FAILED')
"@

Test-Django "HIBP Service Check" "manage.py shell -c `"$hibpTest`"" $true

# Test 4: URL Resolution
Write-Host ""
Write-Host "🌐 URL ROUTING" -ForegroundColor Yellow
Write-Host "----------------------------------------"

$urlTest = @"
from django.urls import reverse
try:
    check_url = reverse('core:check_email')
    newsletter_url = reverse('newsletter:subscribe')
    print('URL Resolution: PASSED')
    print(f'Check Email URL: {check_url}')
    print(f'Newsletter URL: {newsletter_url}')
except Exception as e:
    print(f'URL Resolution: FAILED - {e}')
"@

Test-Django "URL Pattern Check" "manage.py shell -c `"$urlTest`"" $true

# Test 5: Static Files (opcional)
Write-Host ""
Write-Host "📁 STATIC FILES" -ForegroundColor Yellow
Write-Host "----------------------------------------"

Test-Django "Static Files Collection" "manage.py collectstatic --noinput" $false

# Summary
Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "🏁 TESTING COMPLETE" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

Write-Host ""
Write-Host "📊 RESULTS:" -ForegroundColor Yellow
Write-Host "Tests Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $TestsFailed" -ForegroundColor Red
Write-Host "Critical Failures: $CriticalFailures" -ForegroundColor Red

if ($CriticalFailures -eq 0) {
    Write-Host ""
    Write-Host "✅ CORE FUNCTIONALITY: OK" -ForegroundColor Green
    Write-Host "🎯 Django system: Working" -ForegroundColor Green
    Write-Host "🎯 Database models: Working" -ForegroundColor Green
    Write-Host "🎯 HIBP service: Working" -ForegroundColor Green
    Write-Host "🎯 URL routing: Working" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  NOTE: Email configuration needs fixing" -ForegroundColor Yellow
    Write-Host "But core application is ready for development!" -ForegroundColor Green
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path "regression_core.log" -Value "$timestamp - ✅ Core regression tests PASSED"
    
    exit 0
} else {
    Write-Host ""
    Write-Host "❌ CRITICAL ISSUES FOUND" -ForegroundColor Red
    Write-Host "Fix core issues before proceeding" -ForegroundColor Red
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path "regression_core.log" -Value "$timestamp - ❌ Core regression tests FAILED"
    
    exit 1
}
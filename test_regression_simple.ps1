# REGRESSION TESTING SCRIPT - Simple Windows Version
# ==================================================

param(
    [switch]$SkipOptional = $false
)

Write-Host "🚀 STARTING REGRESSION TESTING" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

$TestsPassed = 0
$TestsFailed = 0
$CriticalFailures = 0

function Test-Step {
    param($Name, $Command, $Critical = $true)
    
    Write-Host ""
    Write-Host "[INFO] Testing: $Name" -ForegroundColor Cyan
    
    try {
        $output = Invoke-Expression $Command 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0 -or $null -eq $exitCode) {
            Write-Host "[SUCCESS] $Name - PASSED" -ForegroundColor Green
            $script:TestsPassed++
            return $true
        } else {
            if ($Critical) {
                Write-Host "[ERROR] $Name - FAILED (CRITICAL)" -ForegroundColor Red
                $script:CriticalFailures++
            } else {
                Write-Host "[WARNING] $Name - FAILED (OPTIONAL)" -ForegroundColor Yellow
            }
            $script:TestsFailed++
            return $false
        }
    }
    catch {
        if ($Critical) {
            Write-Host "[ERROR] $Name - FAILED: $($_.Exception.Message)" -ForegroundColor Red
            $script:CriticalFailures++
        } else {
            Write-Host "[WARNING] $Name - FAILED: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        $script:TestsFailed++
        return $false
    }
}

# Step 1: Docker Check
Write-Host ""
Write-Host "Step 1: Environment Check" -ForegroundColor Yellow
Write-Host "-------------------------"

try {
    docker compose ps | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Docker services running" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Starting Docker services..." -ForegroundColor Cyan
        docker compose up -d
        Start-Sleep 10
    }
} catch {
    Write-Host "[ERROR] Docker not available" -ForegroundColor Red
    exit 1
}

# Step 2: Quick Health Check
Write-Host ""
Write-Host "Step 2: Quick Health Check" -ForegroundColor Yellow
Write-Host "---------------------------"

$result = Test-Step "Quick Regression Check" "docker compose exec web python quick_regression_check.py" $true

if (-not $result) {
    Write-Host ""
    Write-Host "❌ CRITICAL: Quick health check failed" -ForegroundColor Red
    Write-Host "Fix issues above before proceeding" -ForegroundColor Red
    exit 1
}

# Step 3: Django System Check
Write-Host ""
Write-Host "Step 3: Django System Check" -ForegroundColor Yellow
Write-Host "----------------------------"

Test-Step "Django System Check" "docker compose exec web python manage.py check" $true

# Step 4: Migration Check
Write-Host ""
Write-Host "Step 4: Migration Status" -ForegroundColor Yellow
Write-Host "------------------------"

Test-Step "Migration Status" "docker compose exec web python manage.py showmigrations" $true

# Step 5: Core Tests
Write-Host ""
Write-Host "Step 5: Core Model Tests" -ForegroundColor Yellow
Write-Host "------------------------"

Test-Step "Newsletter Models" "docker compose exec web python manage.py test newsletter.tests.SubscriberModelTest -v 1" $true

# Step 6: Optional Tests
if (-not $SkipOptional) {
    Write-Host ""
    Write-Host "Step 6: Optional Tests" -ForegroundColor Yellow
    Write-Host "----------------------"
    
    Test-Step "Newsletter Forms" "docker compose exec web python manage.py test newsletter.tests.SubscribeFormTest -v 1" $false
    Test-Step "HIBP Service" "docker compose exec web python manage.py test core.tests.test_hibp_service -v 1" $false
}

# Summary
Write-Host ""
Write-Host "===============================" -ForegroundColor Green
Write-Host "🏁 TESTING COMPLETE" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

Write-Host ""
Write-Host "📊 SUMMARY:" -ForegroundColor Yellow
Write-Host "Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Failed: $TestsFailed" -ForegroundColor Red
Write-Host "Critical Failures: $CriticalFailures" -ForegroundColor Red

if ($CriticalFailures -eq 0) {
    Write-Host ""
    Write-Host "✅ ALL CRITICAL TESTS PASSED!" -ForegroundColor Green
    Write-Host "🚀 Safe to implement new features" -ForegroundColor Green
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp : Regression tests passed"
    $logMessage | Out-File -Append ".regression_test_log"
    
    exit 0
} else {
    Write-Host ""
    Write-Host "❌ CRITICAL TESTS FAILED!" -ForegroundColor Red
    Write-Host "Fix issues before proceeding" -ForegroundColor Red
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp : Regression tests failed ($CriticalFailures failures)"
    $logMessage | Out-File -Append ".regression_test_log"
    
    exit 1
}

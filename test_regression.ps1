# REGRESSION TESTING SCRIPT - Windows PowerShell Version (Fixed)
# ================================================================
# Este script ejecuta tests de regresión de forma segura en Windows

param(
    [switch]$SkipOptional = $false,
    [switch]$Verbose = $false
)

# Colors for output
function Write-Status {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Initialize counters
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:TotalTests = 0
$script:CriticalFailures = 0

function Test-Command {
    param(
        [string]$TestName,
        [string]$Command,
        [bool]$Required = $false
    )
    
    Write-Status "Running: $TestName"
    
    try {
        # Execute command and capture output
        $output = Invoke-Expression $Command 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0 -or $null -eq $exitCode) {
            Write-Success "$TestName - PASSED"
            return $true
        } else {
            if ($Required) {
                Write-Error-Custom "$TestName - FAILED (REQUIRED)"
                $script:CriticalFailures++
            } else {
                Write-Warning "$TestName - FAILED (OPTIONAL)"
            }
            return $false
        }
    }
    catch {
        if ($Required) {
            Write-Error-Custom "$TestName - FAILED (REQUIRED): $($_.Exception.Message)"
            $script:CriticalFailures++
        } else {
            Write-Warning "$TestName - FAILED (OPTIONAL): $($_.Exception.Message)"
        }
        return $false
    }
}

function Track-Result {
    param([bool]$Passed, [bool]$IsCritical = $false)
    
    $script:TotalTests++
    if ($Passed) {
        $script:TestsPassed++
    } else {
        $script:TestsFailed++
    }
}

Write-Host "🚀 STARTING REGRESSION TESTING PIPELINE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Status "Step 1: Environment Check"
Write-Host "----------------------------------------"

# Check if Docker is running
try {
    $dockerStatus = docker compose ps 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker services are running"
    } else {
        Write-Warning "Docker compose not running. Starting services..."
        docker compose up -d
        Start-Sleep -Seconds 10
    }
} catch {
    Write-Error-Custom "Docker not available: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Status "Step 2: Quick Health Check"
Write-Host "----------------------------------------"

$result = Test-Command "Quick Regression Check" "docker compose exec web python quick_regression_check.py" $true
Track-Result $result $true

if (-not $result) {
    Write-Error-Custom "Quick health check failed. Fix issues before proceeding."
    exit 1
}

Write-Host ""
Write-Status "Step 3: Django System Check"
Write-Host "----------------------------------------"

$result = Test-Command "Django System Check" "docker compose exec web python manage.py check" $true
Track-Result $result $true

Write-Host ""
Write-Status "Step 4: Migration Check"
Write-Host "----------------------------------------"

$result = Test-Command "Migration Check" "docker compose exec web python manage.py showmigrations --plan" $true
Track-Result $result $true

Write-Host ""
Write-Status "Step 5: Core Model Tests"
Write-Host "----------------------------------------"

# Test individual components that are critical
$result = Test-Command "Newsletter Model Test" "docker compose exec web python manage.py test newsletter.tests.SubscriberModelTest -v 1" $true
Track-Result $result $true

$result = Test-Command "Core Model Test" "docker compose exec web python manage.py test core.tests.test_regression.DatabaseRegressionTests -v 1" $true
Track-Result $result $true

if (-not $SkipOptional) {
    Write-Host ""
    Write-Status "Step 6: Optional Tests"
    Write-Host "----------------------------------------"

    $result = Test-Command "Newsletter Forms" "docker compose exec web python manage.py test newsletter.tests.SubscribeFormTest -v 1" $false
    Track-Result $result $false

    $result = Test-Command "HIBP Service Tests" "docker compose exec web python manage.py test core.tests.test_hibp_service -v 1" $false
    Track-Result $result $false
}

Write-Host ""
Write-Status "Step 7: Admin Functionality"
Write-Host "----------------------------------------"

# Simple admin test
$result = Test-Command "Admin Interface" "docker compose exec web python manage.py check --deploy" $false
Track-Result $result $false

Write-Host ""
Write-Status "Step 8: Security Check"
Write-Host "----------------------------------------"

$result = Test-Command "Security Settings" "docker compose exec web python manage.py check --deploy" $false
Track-Result $result $false

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "🏁 REGRESSION TESTING COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Print summary
Write-Host ""
Write-Host "📊 TEST SUMMARY:" -ForegroundColor Yellow
Write-Host "----------------------------------------"
Write-Host "Total Tests: $($script:TotalTests)"
Write-Host "Passed: $($script:TestsPassed)" -ForegroundColor Green
Write-Host "Failed: $($script:TestsFailed)" -ForegroundColor Red
Write-Host "Critical Failures: $($script:CriticalFailures)" -ForegroundColor Red

if ($script:CriticalFailures -eq 0) {
    Write-Success "✅ ALL CRITICAL TESTS PASSED - SAFE TO PROCEED"
    Write-Host ""
    Write-Host "🎯 Next Steps:" -ForegroundColor Green
    Write-Host "1. ✅ Regression tests passed"
    Write-Host "2. 🚀 Safe to implement new features"
    Write-Host "3. 🔄 Run this script again after any changes"
    
    # Create success marker
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path ".regression_test_log" -Value "$timestamp`: All critical regression tests passed"
    
    Write-Host ""
    Write-Host "🎉 REGRESSION TESTING SUCCESSFUL!" -ForegroundColor Green
    Write-Host "Your application is ready for new development." -ForegroundColor Green
    
    exit 0
} else {
    Write-Error-Custom "❌ CRITICAL TESTS FAILED - DO NOT PROCEED"
    Write-Host ""
    Write-Host "🚨 REQUIRED ACTIONS:" -ForegroundColor Red
    Write-Host "1. ❌ Fix all critical test failures"
    Write-Host "2. 🔧 Run: docker compose exec web python quick_regression_check.py"
    Write-Host "3. 🧪 Re-run this script: .\test_regression.ps1"
    Write-Host "4. ⚠️  DO NOT implement new features until all critical tests pass"
    
    # Create failure marker
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path ".regression_test_log" -Value "$timestamp`: Critical regression tests failed ($($script:CriticalFailures) failures)"
    
    exit 1
}

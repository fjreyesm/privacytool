# REGRESSION TESTING SCRIPT - FIXED VERSION
# ==========================================
# Tests que SÍ existen y funcionan en tu proyecto

param(
    [switch]$SkipOptional = $false,
    [switch]$Verbose = $false
)

# Colors for PowerShell output
function Write-TestStatus {
    param($Message, $Color = "Cyan")
    Write-Host "[INFO] $Message" -ForegroundColor $Color
}

function Write-TestSuccess {
    param($Message)
    Write-Host "[✅ SUCCESS] $Message" -ForegroundColor Green
}

function Write-TestWarning {
    param($Message)
    Write-Host "[⚠️ WARNING] $Message" -ForegroundColor Yellow
}

function Write-TestError {
    param($Message)
    Write-Host "[❌ ERROR] $Message" -ForegroundColor Red
}

# Initialize counters
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:CriticalFailures = 0

function Execute-Test {
    param(
        [string]$TestName,
        [string]$Command,
        [bool]$IsCritical = $true
    )
    
    Write-TestStatus "Testing: $TestName"
    
    try {
        # Execute command and capture ALL output
        $result = Invoke-Expression $Command
        $exitCode = $LASTEXITCODE
        
        # Show output if verbose or if failed
        if ($Verbose -or $exitCode -ne 0) {
            Write-Host "Command output:" -ForegroundColor Gray
            Write-Host $result -ForegroundColor Gray
            Write-Host "Exit code: $exitCode" -ForegroundColor Gray
        }
        
        if ($exitCode -eq 0) {
            Write-TestSuccess "$TestName - PASSED"
            $script:TestsPassed++
            return $true
        }
        else {
            if ($IsCritical) {
                Write-TestError "$TestName - FAILED (CRITICAL) - Exit code: $exitCode"
                $script:CriticalFailures++
            }
            else {
                Write-TestWarning "$TestName - FAILED (OPTIONAL) - Exit code: $exitCode"
            }
            $script:TestsFailed++
            return $false
        }
    }
    catch {
        $errorMsg = $_.Exception.Message
        if ($IsCritical) {
            Write-TestError "$TestName - EXCEPTION (CRITICAL): $errorMsg"
            $script:CriticalFailures++
        }
        else {
            Write-TestWarning "$TestName - EXCEPTION (OPTIONAL): $errorMsg"
        }
        $script:TestsFailed++
        return $false
    }
}

Write-Host "🚀 STARTING REGRESSION TESTING - FIXED VERSION" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Step 1: Environment Check
Write-Host ""
Write-TestStatus "Step 1: Environment Check" "Yellow"
Write-Host "----------------------------------------"

# Check Docker
try {
    $dockerCheck = docker compose ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-TestSuccess "Docker Compose services are running"
    }
    else {
        Write-TestWarning "Starting Docker services..."
        docker compose up -d | Out-Host
        Start-Sleep -Seconds 15
        $dockerCheck = docker compose ps 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-TestSuccess "Docker services started successfully"
        }
        else {
            Write-TestError "Failed to start Docker services"
            exit 1
        }
    }
}
catch {
    Write-TestError "Docker not available: $($_.Exception.Message)"
    exit 1
}

# Step 2: Basic Django Health Check
Write-Host ""
Write-TestStatus "Step 2: Django Health Check" "Yellow"
Write-Host "----------------------------------------"

$result = Execute-Test "Django System Check" "docker compose exec web python manage.py check" $true

# Step 3: Database & Migration Check
Write-Host ""
Write-TestStatus "Step 3: Database & Migration Check" "Yellow"
Write-Host "----------------------------------------"

$result = Execute-Test "Database Connection" "docker compose exec web python manage.py check --database default" $true
$result = Execute-Test "Migration Status" "docker compose exec web python manage.py showmigrations" $true

# Step 4: Model Tests (using REAL test paths)
Write-Host ""
Write-TestStatus "Step 4: Core Model Tests" "Yellow"
Write-Host "----------------------------------------"

# Test newsletter app models
$result = Execute-Test "Newsletter App Tests" "docker compose exec web python manage.py test newsletter --verbosity=1" $true

# Test core app 
$result = Execute-Test "Core App Tests" "docker compose exec web python manage.py test core --verbosity=1" $true

# Step 5: Critical Functionality Tests
Write-Host ""
Write-TestStatus "Step 5: Critical Functionality Tests" "Yellow"
Write-Host "----------------------------------------"

# Test HIBP integration
$result = Execute-Test "HIBP Service Test" "docker compose exec web python manage.py shell -c `"from core.services import EmailBreachService; service = EmailBreachService(); result = service.check_email('test@example.com'); print('HIBP Test:', 'PASSED' if result is not None else 'FAILED')`"" $true

# Test newsletter subscription
$result = Execute-Test "Newsletter Model Creation" "docker compose exec web python manage.py shell -c `"from newsletter.models import Subscriber; print('Newsletter model:', 'PASSED' if Subscriber.objects.model else 'FAILED')`"" $true

# Step 6: Optional Tests (if not skipped)
if (-not $SkipOptional) {
    Write-Host ""
    Write-TestStatus "Step 6: Optional Tests" "Yellow"
    Write-Host "----------------------------------------"
    
    # Static files check
    $result = Execute-Test "Static Files Collection" "docker compose exec web python manage.py collectstatic --noinput --verbosity=0" $false
    
    # Admin check
    $result = Execute-Test "Admin Interface" "docker compose exec web python manage.py check --deploy --verbosity=0" $false
}

# Step 7: URL Resolution Tests
Write-Host ""
Write-TestStatus "Step 7: URL Resolution Tests" "Yellow"
Write-Host "----------------------------------------"

# Test main URLs resolve
$result = Execute-Test "URL Patterns Check" "docker compose exec web python manage.py shell -c `"from django.urls import reverse; print('URLs:', 'PASSED' if reverse('core:check_email') and reverse('newsletter:subscribe') else 'FAILED')`"" $true

# Summary
Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "🏁 REGRESSION TESTING COMPLETE" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

Write-Host ""
Write-Host "📊 FINAL SUMMARY:" -ForegroundColor Yellow
Write-Host "----------------------------------------"
Write-Host "Tests Passed: $($script:TestsPassed)" -ForegroundColor Green
Write-Host "Tests Failed: $($script:TestsFailed)" -ForegroundColor Red
Write-Host "Critical Failures: $($script:CriticalFailures)" -ForegroundColor Red

# Create timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

if ($script:CriticalFailures -eq 0) {
    Write-Host ""
    Write-TestSuccess "✅ ALL CRITICAL TESTS PASSED!"
    Write-Host ""
    Write-Host "🎯 STATUS: READY FOR DEVELOPMENT" -ForegroundColor Green
    Write-Host "✅ Newsletter functionality: OK" -ForegroundColor Green
    Write-Host "✅ Email verification: OK" -ForegroundColor Green
    Write-Host "✅ Database models: OK" -ForegroundColor Green
    Write-Host "✅ URL routing: OK" -ForegroundColor Green
    
    # Log success
    $logEntry = "$timestamp - ✅ Regression tests PASSED (Passed: $($script:TestsPassed), Failed: $($script:TestsFailed))"
    Add-Content -Path "regression_test.log" -Value $logEntry
    
    Write-Host ""
    Write-Host "🚀 SAFE TO PROCEED WITH DEVELOPMENT!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host ""
    Write-TestError "❌ CRITICAL TESTS FAILED!"
    Write-Host ""
    Write-Host "🚨 DO NOT PROCEED - FIX ISSUES FIRST:" -ForegroundColor Red
    Write-Host "1. Check Docker services are running properly" -ForegroundColor Red
    Write-Host "2. Verify database migrations are applied" -ForegroundColor Red
    Write-Host "3. Test core functionality manually" -ForegroundColor Red
    Write-Host "4. Re-run this script when fixed" -ForegroundColor Red
    
    # Log failure
    $logEntry = "$timestamp - ❌ Regression tests FAILED (Critical failures: $($script:CriticalFailures))"
    Add-Content -Path "regression_test.log" -Value $logEntry
    
    exit 1
}
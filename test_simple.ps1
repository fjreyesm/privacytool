Write-Host "🚀 REGRESSION TEST SIMPLE" -ForegroundColor Green

Write-Host "Step 1: Quick Health Check" -ForegroundColor Yellow
docker compose exec web python quick_regression_check.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ HEALTH CHECK PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ HEALTH CHECK FAILED" -ForegroundColor Red
    exit 1
}

Write-Host "Step 2: Django System Check" -ForegroundColor Yellow
docker compose exec web python manage.py check
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SYSTEM CHECK PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ SYSTEM CHECK FAILED" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "🚀 Safe to implement new features" -ForegroundColor Green

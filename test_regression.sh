#!/bin/bash

# REGRESSION TESTING SCRIPT
# ==========================
# Este script debe ejecutarse ANTES de implementar cualquier nueva funcionalidad
# y DESPUÉS de cualquier cambio para garantizar que no se rompa funcionalidad existente.

set -e  # Exit on any error

echo "🚀 STARTING REGRESSION TESTING PIPELINE"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run command and check result
run_test() {
    local test_name="$1"
    local command="$2"
    local required="$3"  # true/false - is this test required to pass?
    
    print_status "Running: $test_name"
    
    if eval "$command"; then
        print_success "$test_name - PASSED"
        return 0
    else
        if [[ "$required" == "true" ]]; then
            print_error "$test_name - FAILED (REQUIRED)"
            return 1
        else
            print_warning "$test_name - FAILED (OPTIONAL)"
            return 0
        fi
    fi
}

# Initialize counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0
CRITICAL_FAILURES=0

# Function to track test results
track_result() {
    local result=$1
    local is_critical=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ $result -eq 0 ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        if [[ "$is_critical" == "true" ]]; then
            CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
        fi
    fi
}

echo ""
print_status "Step 1: Environment Check"
echo "----------------------------------------"

# Check if Docker is running
if ! docker compose ps &> /dev/null; then
    print_error "Docker compose not running. Starting services..."
    docker compose up -d
    sleep 10
fi

print_success "Docker services are running"

echo ""
print_status "Step 2: Database Migration Check"
echo "----------------------------------------"

# Check migrations
run_test "Database Migration Check" "docker compose exec web python manage.py migrate --check" "true"
track_result $? "true"

echo ""
print_status "Step 3: Django System Check"
echo "----------------------------------------"

# System check
run_test "Django System Check" "docker compose exec web python manage.py check" "true"
track_result $? "true"

echo ""
print_status "Step 4: Critical Regression Tests"
echo "----------------------------------------"

# Run regression tests first (most important)
run_test "Regression Test Suite" "docker compose exec web python manage.py test core.tests.test_regression -v 1" "true"
track_result $? "true"

echo ""
print_status "Step 5: Core Functionality Tests"
echo "----------------------------------------"

# Test individual components
run_test "Newsletter Models" "docker compose exec web python manage.py test newsletter.tests.SubscriberModelTest -v 1" "true"
track_result $? "true"

run_test "Newsletter Forms" "docker compose exec web python manage.py test newsletter.tests.SubscribeFormTest -v 1" "false"
track_result $? "false"

run_test "Newsletter Views" "docker compose exec web python manage.py test newsletter.tests.NewsletterViewsTest -v 1" "false"
track_result $? "false"

echo ""
print_status "Step 6: Security Tests"
echo "----------------------------------------"

run_test "Security Tests" "docker compose exec web python manage.py test newsletter.tests.SecurityTest -v 1" "true"
track_result $? "true"

echo ""
print_status "Step 7: Performance Tests"
echo "----------------------------------------"

run_test "Performance Tests" "docker compose exec web python manage.py test newsletter.tests.PerformanceTest -v 1" "false"
track_result $? "false"

echo ""
print_status "Step 8: HIBP Service Tests"
echo "----------------------------------------"

run_test "HIBP Service Tests" "docker compose exec web python manage.py test core.tests.test_hibp_service -v 1" "false"
track_result $? "false"

echo ""
print_status "Step 9: Admin Interface Tests"
echo "----------------------------------------"

run_test "Admin Registration Check" "docker compose exec web python manage.py shell -c \"
from django.contrib import admin
from newsletter.models import Subscriber
print('Admin models:', [m.__name__ for m in admin.site._registry.keys()])
assert Subscriber in admin.site._registry, 'Subscriber not in admin'
print('✅ Admin registration OK')
\"" "true"
track_result $? "true"

echo ""
print_status "Step 10: Template Rendering Tests"
echo "----------------------------------------"

run_test "Template Syntax Check" "docker compose exec web python manage.py shell -c \"
from django.template.loader import get_template
templates = ['base.html', 'newsletter/subscribe.html', 'verification/check.html']
for template in templates:
    try:
        t = get_template(template)
        print(f'✅ {template} OK')
    except Exception as e:
        print(f'❌ {template} ERROR: {e}')
        raise
\"" "true"
track_result $? "true"

echo ""
print_status "Step 11: URL Configuration Tests"
echo "----------------------------------------"

run_test "URL Resolution Check" "docker compose exec web python manage.py shell -c \"
from django.urls import reverse
urls_to_test = [
    ('core:index', 'Homepage'),
    ('core:verification_home', 'Verification'),
    ('newsletter:subscribe', 'Newsletter'),
]
for url_name, description in urls_to_test:
    try:
        url = reverse(url_name)
        print(f'✅ {description} URL ({url_name}) OK')
    except Exception as e:
        print(f'❌ {description} URL ({url_name}) ERROR: {e}')
\"" "false"
track_result $? "false"

echo ""
print_status "Step 12: Static Files Check"
echo "----------------------------------------"

run_test "Static Files Collection" "docker compose exec web python manage.py collectstatic --noinput --dry-run" "false"
track_result $? "false"

echo ""
print_status "Step 13: Database Integrity Check"
echo "----------------------------------------"

run_test "Database Integrity" "docker compose exec web python manage.py shell -c \"
from newsletter.models import Subscriber
from core.models.verification import Verification
print(f'Subscribers: {Subscriber.objects.count()}')
print(f'Verifications: {Verification.objects.count()}')
print('✅ Database accessible')
\"" "true"
track_result $? "true"

echo ""
echo "========================================"
echo "🏁 REGRESSION TESTING COMPLETE"
echo "========================================"

# Print summary
echo ""
echo "📊 TEST SUMMARY:"
echo "----------------------------------------"
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo "Critical Failures: $CRITICAL_FAILURES"

if [ $CRITICAL_FAILURES -eq 0 ]; then
    print_success "✅ ALL CRITICAL TESTS PASSED - SAFE TO PROCEED"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. ✅ Regression tests passed"
    echo "2. 🚀 Safe to implement new features"
    echo "3. 🔄 Run this script again after any changes"
    
    # Create success marker
    echo "$(date): All critical regression tests passed" >> .regression_test_log
    
    exit 0
else
    print_error "❌ CRITICAL TESTS FAILED - DO NOT PROCEED"
    echo ""
    echo "🚨 REQUIRED ACTIONS:"
    echo "1. ❌ Fix all critical test failures"
    echo "2. 🔧 Run regression analysis: python fix_regression_issues.py"
    echo "3. 🧪 Re-run this script: ./test_regression.sh"
    echo "4. ⚠️  DO NOT implement new features until all critical tests pass"
    
    # Create failure marker
    echo "$(date): Critical regression tests failed ($CRITICAL_FAILURES failures)" >> .regression_test_log
    
    exit 1
fi

# Performance report (if all tests passed)
echo ""
print_status "📈 Performance Report"
echo "----------------------------------------"
docker compose exec web python manage.py shell -c "
import time
from django.test.utils import override_settings
from django.test import Client

client = Client()
urls_to_test = ['/', '/newsletter/', '/verification/']

print('URL Performance Test:')
for url in urls_to_test:
    start = time.time()
    try:
        response = client.get(url)
        end = time.time()
        status = response.status_code
        elapsed = (end - start) * 1000
        print(f'{url:20} {status:3d} {elapsed:6.1f}ms')
    except Exception as e:
        print(f'{url:20} ERR {str(e)[:30]}')
"

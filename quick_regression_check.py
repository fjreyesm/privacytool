#!/usr/bin/env python3
"""
Quick Regression Check
====================
Verifica funcionalidad básica del sistema Django
"""

import os
import sys
import django

# Setup Django - CORREGIDO: usar 'securecheck.settings' no 'securecheck_fixed.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securecheck.settings')
django.setup()

def test_database_connection():
    """Test database connectivity"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_models():
    """Test core models load properly"""
    try:
        from newsletter.models import Subscriber
        from core.models import EmailVerification
        print("✅ Models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_hibp_service():
    """Test HIBP service basic functionality"""
    try:
        from core.services import EmailBreachService
        service = EmailBreachService()
        # Just test that service can be instantiated
        print("✅ HIBP service initialized")
        return True
    except Exception as e:
        print(f"❌ HIBP service failed: {e}")
        return False

def test_urls():
    """Test URL patterns can be resolved"""
    try:
        from django.urls import reverse
        reverse('core:check_email')
        reverse('newsletter:subscribe')
        print("✅ URL patterns working")
        return True
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        return False

def main():
    """Run all quick regression checks"""
    print("🚀 Starting Quick Regression Check")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Model Loading", test_models),
        ("HIBP Service", test_hibp_service),
        ("URL Patterns", test_urls),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[INFO] Testing: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"[✅ SUCCESS] {test_name}")
            else:
                print(f"[❌ FAILED] {test_name}")
        except Exception as e:
            print(f"[❌ ERROR] {test_name}: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL QUICK CHECKS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME CHECKS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()

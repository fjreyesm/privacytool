#!/usr/bin/env python3
"""
QUICK REGRESSION ANALYSIS - Container Version
============================================

Versión simplificada que se ejecuta dentro del container Docker
para analizar rápidamente problemas de regresión.

Usage:
    docker compose exec web python quick_regression_check.py

"""

import os
import sys
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securecheck.settings')
django.setup()

def check_system_health():
    """Quick system health check"""
    print("🔍 QUICK REGRESSION ANALYSIS")
    print("=" * 40)
    
    issues_found = []
    
    try:
        # Check 1: Basic imports work
        print("\n1. Testing basic imports...")
        try:
            from django.conf import settings
            from django.urls import reverse
            from newsletter.models import Subscriber
            from core.models.verification import Verification
            print("   ✅ All imports work")
        except ImportError as e:
            print(f"   ❌ Import error: {e}")
            issues_found.append(f"Import error: {e}")
        
        # Check 2: URL resolution
        print("\n2. Testing URL resolution...")
        try:
            from django.urls import reverse
            urls_to_test = [
                ('core:verification_home', 'Verification page'),
                ('newsletter:subscribe', 'Newsletter page'),
            ]
            
            for url_name, description in urls_to_test:
                try:
                    url = reverse(url_name)
                    print(f"   ✅ {description}: {url}")
                except Exception as e:
                    print(f"   ❌ {description}: {e}")
                    issues_found.append(f"URL error {url_name}: {e}")
                    
        except Exception as e:
            print(f"   ❌ URL resolution failed: {e}")
            issues_found.append(f"URL resolution: {e}")
        
        # Check 3: Database connectivity
        print("\n3. Testing database...")
        try:
            from newsletter.models import Subscriber
            count = Subscriber.objects.count()
            print(f"   ✅ Database accessible ({count} subscribers)")
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            issues_found.append(f"Database error: {e}")
        
        # Check 4: Admin registration
        print("\n4. Testing admin registration...")
        try:
            from django.contrib import admin
            from newsletter.models import Subscriber, NewsletterCampaign
            
            registered_models = [model._meta.model for model, admin_class in admin.site._registry.items()]
            
            if Subscriber in registered_models:
                print("   ✅ Subscriber registered in admin")
            else:
                print("   ❌ Subscriber not registered in admin")
                issues_found.append("Subscriber not in admin")
                
            if NewsletterCampaign in registered_models:
                print("   ✅ NewsletterCampaign registered in admin")
            else:
                print("   ❌ NewsletterCampaign not registered in admin")
                issues_found.append("NewsletterCampaign not in admin")
                
        except Exception as e:
            print(f"   ❌ Admin check failed: {e}")
            issues_found.append(f"Admin check: {e}")
        
        # Check 5: Template loading
        print("\n5. Testing template loading...")
        try:
            from django.template.loader import get_template
            templates_to_test = [
                'base.html',
                'newsletter/subscribe.html',
                'verification/check.html'
            ]
            
            for template in templates_to_test:
                try:
                    get_template(template)
                    print(f"   ✅ {template}")
                except Exception as e:
                    print(f"   ❌ {template}: {e}")
                    issues_found.append(f"Template {template}: {e}")
                    
        except Exception as e:
            print(f"   ❌ Template check failed: {e}")
            issues_found.append(f"Template check: {e}")
        
        # Check 6: Form validation
        print("\n6. Testing form validation...")
        try:
            from newsletter.forms import SubscribeForm
            
            # Test valid form
            form_data = {
                'email': 'test@example.com',
                'first_name': 'Test',
                'interests': ['privacy'],
                'privacy_consent': True
            }
            
            form = SubscribeForm(data=form_data)
            if form.is_valid():
                print("   ✅ SubscribeForm validation works")
            else:
                print(f"   ❌ SubscribeForm validation failed: {form.errors}")
                issues_found.append(f"Form validation: {form.errors}")
                
        except Exception as e:
            print(f"   ❌ Form test failed: {e}")
            issues_found.append(f"Form test: {e}")
        
        # Check 7: HIBP Service
        print("\n7. Testing HIBP service...")
        try:
            from core.services.hibp_service import HIBPService
            service = HIBPService()
            print("   ✅ HIBP service imports correctly")
        except Exception as e:
            print(f"   ❌ HIBP service error: {e}")
            issues_found.append(f"HIBP service: {e}")
        
        # Summary
        print("\n" + "=" * 40)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 40)
        
        if not issues_found:
            print("✅ NO CRITICAL ISSUES FOUND!")
            print("🚀 Safe to proceed with development")
            return True
        else:
            print(f"❌ FOUND {len(issues_found)} ISSUES:")
            for i, issue in enumerate(issues_found, 1):
                print(f"   {i}. {issue}")
            
            print("\n🔧 RECOMMENDED FIXES:")
            if any("URL error" in issue for issue in issues_found):
                print("   • Check urls.py files for missing patterns")
            if any("Template" in issue for issue in issues_found):
                print("   • Create missing template files")
            if any("admin" in issue for issue in issues_found):
                print("   • Check admin.py registrations")
            if any("Form validation" in issue for issue in issues_found):
                print("   • Review form field definitions")
            if any("Database" in issue for issue in issues_found):
                print("   • Run: python manage.py migrate")
            
            return False
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_basic_tests():
    """Run basic Django tests that should always pass"""
    print("\n🧪 RUNNING BASIC TESTS")
    print("=" * 40)
    
    try:
        # Test 1: System check
        print("\n1. Django system check...")
        from django.core.management import call_command
        from io import StringIO
        import sys
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            call_command('check')
            sys.stdout = old_stdout
            print("   ✅ System check passed")
        except Exception as e:
            sys.stdout = old_stdout
            print(f"   ❌ System check failed: {e}")
            return False
        
        # Test 2: Migration check
        print("\n2. Migration check...")
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            call_command('showmigrations', '--plan')
            output = mystdout.getvalue()
            sys.stdout = old_stdout
            
            if '[ ]' not in output:
                print("   ✅ All migrations applied")
            else:
                print("   ❌ Unapplied migrations found")
                print("   Run: python manage.py migrate")
                return False
        except Exception as e:
            sys.stdout = old_stdout
            print(f"   ❌ Migration check failed: {e}")
            return False
        
        # Test 3: Basic model test
        print("\n3. Model creation test...")
        try:
            from newsletter.models import Subscriber
            from django.db import transaction
            
            with transaction.atomic():
                # Create test subscriber
                test_email = 'regression_test@example.com'
                Subscriber.objects.filter(email=test_email).delete()
                
                subscriber = Subscriber.objects.create(
                    email=test_email,
                    first_name='Regression Test'
                )
                
                if subscriber.pk:
                    print("   ✅ Model creation works")
                    subscriber.delete()  # Cleanup
                    return True
                else:
                    print("   ❌ Model creation failed")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Model test failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test execution failed: {e}")
        return False

def run_simple_functional_tests():
    """Run simple functional tests"""
    print("\n🎯 RUNNING FUNCTIONAL TESTS")
    print("=" * 40)
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
        client = Client()
        
        # Test 1: Home page
        print("\n1. Testing home page...")
        try:
            response = client.get('/')
            if response.status_code in [200, 302]:
                print(f"   ✅ Home page accessible (status: {response.status_code})")
            else:
                print(f"   ❌ Home page error (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"   ❌ Home page test failed: {e}")
            return False
        
        # Test 2: Newsletter page
        print("\n2. Testing newsletter page...")
        try:
            response = client.get('/newsletter/')
            if response.status_code in [200, 302]:
                print(f"   ✅ Newsletter page accessible (status: {response.status_code})")
            else:
                print(f"   ❌ Newsletter page error (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"   ❌ Newsletter page test failed: {e}")
            return False
        
        # Test 3: Verification page
        print("\n3. Testing verification page...")
        try:
            response = client.get('/verification/')
            if response.status_code in [200, 302]:
                print(f"   ✅ Verification page accessible (status: {response.status_code})")
            else:
                print(f"   ❌ Verification page error (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"   ❌ Verification page test failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Functional tests failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING QUICK REGRESSION CHECK")
    print("=" * 50)
    
    # Run system health check
    health_ok = check_system_health()
    
    # Run basic tests
    tests_ok = run_basic_tests()
    
    # Run functional tests
    functional_ok = run_simple_functional_tests()
    
    print("\n" + "=" * 50)
    print("🏁 QUICK CHECK COMPLETE")
    print("=" * 50)
    
    if health_ok and tests_ok and functional_ok:
        print("✅ SYSTEM HEALTHY - Ready for full regression tests")
        print("\nNext steps:")
        print("1. Run PowerShell suite: .\\test_regression.ps1")
        print("2. Run specific tests: docker compose exec web python manage.py test")
        print("3. Safe to implement new features")
        exit(0)
    else:
        print("❌ ISSUES FOUND - Fix before proceeding")
        print("\nImmediate actions:")
        print("1. Fix issues listed above")
        print("2. Re-run this check: docker compose exec web python quick_regression_check.py")
        print("3. Only proceed when this check passes")
        exit(1)

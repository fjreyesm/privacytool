#!/usr/bin/env python3
"""
QUICK REGRESSION ANALYSIS - Container Version
============================================

Versión simplificada que se ejecuta dentro del container Docker
para analizar rápidamente problemas de regresión.

Usage:
    docker compose exec web python quick_regression_check.py

"""

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
            print("1. Run: python manage.py migrate")
            print("2. Check URLs in urls.py files")
            print("3. Verify template files exist")
            print("4. Check admin.py registrations")
            print("5. Review form definitions")
            
            return False
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        return False

def run_basic_tests():
    """Run basic Django tests that should always pass"""
    print("\n🧪 RUNNING BASIC TESTS")
    print("=" * 40)
    
    try:
        import subprocess
        import sys
        
        # Test 1: System check
        print("\n1. Django system check...")
        result = subprocess.run([
            sys.executable, 'manage.py', 'check'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ System check passed")
        else:
            print(f"   ❌ System check failed:")
            print(f"   {result.stderr}")
            return False
        
        # Test 2: Migration check
        print("\n2. Migration check...")
        result = subprocess.run([
            sys.executable, 'manage.py', 'showmigrations', '--plan'
        ], capture_output=True, text=True)
        
        if '[ ]' not in result.stdout:
            print("   ✅ All migrations applied")
        else:
            print("   ❌ Unapplied migrations found")
            print("   Run: python manage.py migrate")
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

if __name__ == "__main__":
    print("🚀 STARTING QUICK REGRESSION CHECK")
    print("=" * 50)
    
    # Run system health check
    health_ok = check_system_health()
    
    # Run basic tests
    tests_ok = run_basic_tests()
    
    print("\n" + "=" * 50)
    print("🏁 QUICK CHECK COMPLETE")
    print("=" * 50)
    
    if health_ok and tests_ok:
        print("✅ SYSTEM HEALTHY - Ready for full regression tests")
        print("\nNext steps:")
        print("1. Run full test suite: python manage.py test")
        print("2. Run regression tests: python manage.py test core.tests.test_regression")
        exit(0)
    else:
        print("❌ ISSUES FOUND - Fix before proceeding")
        print("\nImmediate actions:")
        print("1. Fix issues listed above")
        print("2. Re-run this check: python quick_regression_check.py")
        print("3. Only proceed when this check passes")
        exit(1)

#!/usr/bin/env python3
"""
REGRESSION FIX SCRIPT
====================

Este script identifica y corrige automáticamente errores de regresión
detectados en la suite de tests.

Usage:
    python manage.py shell < fix_regression_issues.py

"""

import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securecheck.settings')
django.setup()

def fix_url_reverse_issues():
    """
    Fix 1: NoReverseMatch errors for 'home' URL
    """
    print("🔧 Fixing URL reverse issues...")
    
    # Check if 'home' URL exists in main urls.py
    try:
        from django.urls import reverse
        reverse('core:index')  # Try core:index instead of 'home'
        print("✅ Core index URL exists")
        return 'core:index'
    except:
        try:
            reverse('index')
            print("✅ Index URL exists")
            return 'index'
        except:
            print("❌ No index URL found")
            return None

def check_missing_templates():
    """
    Fix 2: Check for missing email templates
    """
    print("\n🔧 Checking email templates...")
    
    from django.template.loader import get_template
    from django.template import TemplateDoesNotExist
    
    required_templates = [
        'newsletter/emails/confirmation.html',
        'newsletter/emails/welcome.html',
        'newsletter/confirmation_success.html',
        'newsletter/unsubscribe_confirm.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        try:
            get_template(template)
            print(f"✅ {template} exists")
        except TemplateDoesNotExist:
            print(f"❌ {template} missing")
            missing_templates.append(template)
    
    return missing_templates

def check_form_validation_issues():
    """
    Fix 3: Check form validation issues
    """
    print("\n🔧 Checking form validation...")
    
    from newsletter.forms import SubscribeForm
    
    # Test with data that should be valid
    test_data = {
        'email': 'test@example.com',
        'first_name': 'Test User',
        'interests': ['privacy'],
        'privacy_consent': True
    }
    
    form = SubscribeForm(data=test_data)
    if form.is_valid():
        print("✅ SubscribeForm validation working")
        return True
    else:
        print(f"❌ SubscribeForm validation failing: {form.errors}")
        return False

def check_database_constraints():
    """
    Fix 4: Check database constraint issues
    """
    print("\n🔧 Checking database constraints...")
    
    from newsletter.models import Subscriber
    from django.db import IntegrityError
    
    try:
        # Try to create a test subscriber
        test_email = 'constraint_test@example.com'
        
        # Clean up any existing
        Subscriber.objects.filter(email=test_email).delete()
        
        # Create first subscriber
        subscriber1 = Subscriber.objects.create(email=test_email)
        print(f"✅ Created subscriber: {subscriber1.email}")
        
        # Try to create duplicate (should fail)
        try:
            subscriber2 = Subscriber.objects.create(email=test_email)
            print("❌ Duplicate email constraint not working")
            return False
        except IntegrityError:
            print("✅ Email uniqueness constraint working")
            return True
        finally:
            # Cleanup
            Subscriber.objects.filter(email=test_email).delete()
            
    except Exception as e:
        print(f"❌ Database constraint test failed: {e}")
        return False

def check_missing_migrations():
    """
    Fix 5: Check for missing migrations
    """
    print("\n🔧 Checking migrations...")
    
    from django.core.management import call_command
    from io import StringIO
    import sys
    
    # Capture output
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    
    try:
        call_command('showmigrations', '--plan')
        output = mystdout.getvalue()
        sys.stdout = old_stdout
        
        if '[ ]' in output:
            print("❌ Unapplied migrations found")
            print("Run: python manage.py migrate")
            return False
        else:
            print("✅ All migrations applied")
            return True
            
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ Migration check failed: {e}")
        return False

def check_admin_configuration():
    """
    Fix 6: Check admin configuration
    """
    print("\n🔧 Checking admin configuration...")
    
    try:
        from django.contrib import admin
        from newsletter.models import Subscriber, NewsletterCampaign, NewsletterTemplate
        
        # Check if models are registered
        registered_models = [model._meta.model for model, admin_class in admin.site._registry.items()]
        
        required_models = [Subscriber, NewsletterCampaign, NewsletterTemplate]
        
        for model in required_models:
            if model in registered_models:
                print(f"✅ {model.__name__} registered in admin")
            else:
                print(f"❌ {model.__name__} not registered in admin")
                
        return True
        
    except Exception as e:
        print(f"❌ Admin check failed: {e}")
        return False

def generate_fix_recommendations():
    """
    Generate specific fix recommendations based on issues found
    """
    print("\n" + "="*50)
    print("🛠️  FIX RECOMMENDATIONS")
    print("="*50)
    
    recommendations = []
    
    # Check issues
    home_url = fix_url_reverse_issues()
    missing_templates = check_missing_templates()
    form_valid = check_form_validation_issues()
    db_constraints = check_database_constraints()
    migrations_ok = check_missing_migrations()
    admin_ok = check_admin_configuration()
    
    # Generate recommendations
    if not home_url:
        recommendations.append({
            'issue': 'NoReverseMatch for "home" URL',
            'fix': 'Add URL pattern: path("", views.index, name="index") to main urls.py',
            'priority': 'HIGH'
        })
    
    if missing_templates:
        for template in missing_templates:
            recommendations.append({
                'issue': f'Missing template: {template}',
                'fix': f'Create template file at templates/{template}',
                'priority': 'HIGH'
            })
    
    if not form_valid:
        recommendations.append({
            'issue': 'SubscribeForm validation failing',
            'fix': 'Check form field definitions and validation rules',
            'priority': 'MEDIUM'
        })
    
    if not db_constraints:
        recommendations.append({
            'issue': 'Database constraint issues',
            'fix': 'Run migrations and check model definitions',
            'priority': 'HIGH'
        })
    
    if not migrations_ok:
        recommendations.append({
            'issue': 'Unapplied migrations',
            'fix': 'Run: python manage.py migrate',
            'priority': 'CRITICAL'
        })
    
    # Print recommendations
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['priority']} - {rec['issue']}")
            print(f"   Fix: {rec['fix']}")
    else:
        print("\n✅ No critical issues found!")
    
    return recommendations

def create_quick_fixes():
    """
    Create quick fix files for common issues
    """
    print("\n🔧 Creating quick fix files...")
    
    # Quick fix for missing home URL
    url_fix = '''
# Add this to your main securecheck/urls.py

from django.urls import path, include
from core.views.dashboard_views import index

urlpatterns = [
    # Add this line if missing:
    path('', index, name='home'),  # or name='index'
    
    # Existing patterns...
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('newsletter/', include('newsletter.urls')),
]
'''
    
    with open('REGRESSION_FIXES.md', 'w') as f:
        f.write("# REGRESSION FIXES\n\n")
        f.write("## URL Fix\n")
        f.write("```python")
        f.write(url_fix)
        f.write("```\n\n")
        
        f.write("## Commands to run:\n")
        f.write("```bash\n")
        f.write("# 1. Apply migrations\n")
        f.write("python manage.py migrate\n\n")
        f.write("# 2. Run regression tests\n")
        f.write("python manage.py test core.tests.test_regression -v 2\n\n")
        f.write("# 3. Run all tests\n")
        f.write("python manage.py test -v 2\n")
        f.write("```\n")
    
    print("✅ Created REGRESSION_FIXES.md with fix instructions")

if __name__ == "__main__":
    print("🚀 REGRESSION ANALYSIS STARTING...")
    print("="*50)
    
    # Run all checks
    recommendations = generate_fix_recommendations()
    
    # Create fix files
    create_quick_fixes()
    
    print("\n" + "="*50)
    print("✅ REGRESSION ANALYSIS COMPLETE")
    print("="*50)
    
    if recommendations:
        print(f"\n⚠️  Found {len(recommendations)} issues that need fixing")
        print("📄 Check REGRESSION_FIXES.md for detailed instructions")
    else:
        print("\n🎉 No critical regression issues found!")
    
    print("\n📊 Next steps:")
    print("1. Fix the issues listed above")
    print("2. Run: python manage.py test core.tests.test_regression")
    print("3. Only proceed with new features after all regression tests pass")

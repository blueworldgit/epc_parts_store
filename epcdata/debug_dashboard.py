#!/usr/bin/env python3
"""
Oscar Dashboard Diagnostic Script
This script helps diagnose common issues with Oscar dashboard login
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
sys.path.append(str(Path(__file__).parent))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

def check_dashboard_config():
    """Check Oscar dashboard configuration"""
    print("=== Oscar Dashboard Configuration Check ===\n")
    
    # Check settings
    from django.conf import settings
    print(f"DEBUG mode: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # Check installed apps
    print(f"\nInstalled Apps: {len(settings.INSTALLED_APPS)} apps")
    oscar_apps = [app for app in settings.INSTALLED_APPS if 'oscar' in app]
    print(f"Oscar Apps: {len(oscar_apps)}")
    for app in oscar_apps:
        print(f"  - {app}")
    
    # Check database connection
    print("\n=== Database Connection ===")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    # Check for users
    print("\n=== User Account Check ===")
    try:
        from django.contrib.auth.models import User
        superuser_count = User.objects.filter(is_superuser=True).count()
        total_users = User.objects.count()
        print(f"Total users: {total_users}")
        print(f"Superusers: {superuser_count}")
        
        if superuser_count == 0:
            print("⚠️  No superuser found. Create one with: python manage.py createsuperuser")
        else:
            print("✓ Superuser exists")
    except Exception as e:
        print(f"✗ User check failed: {e}")
    
    # Check static files
    print("\n=== Static Files Check ===")
    static_root = Path(settings.STATIC_ROOT) if settings.STATIC_ROOT else None
    if static_root and static_root.exists():
        print(f"✓ Static root exists: {static_root}")
        static_files = list(static_root.rglob('*'))
        print(f"  Static files found: {len(static_files)}")
    else:
        print("⚠️  Static files not collected. Run: python manage.py collectstatic")
    
    # Check templates
    print("\n=== Template Check ===")
    template_dirs = settings.TEMPLATES[0]['DIRS']
    for template_dir in template_dirs:
        template_path = Path(template_dir)
        if template_path.exists():
            print(f"✓ Template directory exists: {template_path}")
            oscar_templates = list(template_path.rglob('*oscar*'))
            dashboard_templates = list(template_path.rglob('*dashboard*'))
            print(f"  Oscar templates: {len(oscar_templates)}")
            print(f"  Dashboard templates: {len(dashboard_templates)}")
        else:
            print(f"✗ Template directory missing: {template_path}")
    
    # Check Oscar URLs
    print("\n=== URL Configuration Check ===")
    try:
        from django.urls import reverse
        dashboard_url = reverse('dashboard:index')
        print(f"✓ Dashboard URL resolved: {dashboard_url}")
    except Exception as e:
        print(f"✗ Dashboard URL resolution failed: {e}")
    
    print("\n=== Recommendations ===")
    print("1. Ensure PostgreSQL is running and accessible")
    print("2. Run 'python manage.py migrate' to apply database migrations")
    print("3. Run 'python manage.py collectstatic' to collect static files")
    print("4. Create a superuser with 'python manage.py createsuperuser'")
    print("5. Check browser console for JavaScript errors")
    print("6. Enable DEBUG=True to see detailed error messages")
    
    return True

if __name__ == '__main__':
    check_dashboard_config()

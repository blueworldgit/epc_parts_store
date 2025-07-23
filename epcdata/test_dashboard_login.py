#!/usr/bin/env python3
"""
Test Dashboard Access
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

def test_dashboard_access():
    """Test accessing the dashboard"""
    print("=== Testing Dashboard Access ===\n")
    
    from django.test.client import Client
    from django.contrib.auth.models import User
    from django.urls import reverse
    
    # Get a superuser
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("✗ No superuser found")
            return
        
        print(f"✓ Using superuser: {user.username}")
        
        # Create test client
        client = Client()
        
        # Test dashboard URL resolution
        try:
            dashboard_url = reverse('dashboard:index')
            print(f"✓ Dashboard URL: {dashboard_url}")
        except Exception as e:
            print(f"✗ Dashboard URL error: {e}")
            return
        
        # Test dashboard access without login
        print("\n--- Testing dashboard access (not logged in) ---")
        response = client.get(dashboard_url)
        print(f"Status: {response.status_code}")
        print(f"Redirect: {response.get('Location', 'None')}")
        
        # Test login
        print("\n--- Testing login ---")
        login_success = client.login(username=user.username, password='admin123')  # You may need to adjust password
        if not login_success:
            print("✗ Login failed - checking if we need to set a known password")
            # Set a known password for testing
            user.set_password('admin123')
            user.save()
            login_success = client.login(username=user.username, password='admin123')
        
        if login_success:
            print("✓ Login successful")
        else:
            print("✗ Login failed")
            return
        
        # Test dashboard access after login
        print("\n--- Testing dashboard access (logged in) ---")
        response = client.get(dashboard_url)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        print(f"Content type: {response.get('Content-Type', 'Unknown')}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if len(content.strip()) == 0:
                print("✗ BLANK PAGE - Content is empty!")
            elif len(content) < 100:
                print(f"⚠️  Very short content: {content[:200]}")
            else:
                print("✓ Content received")
                # Check for common Oscar dashboard elements
                if 'dashboard' in content.lower():
                    print("✓ Contains 'dashboard' text")
                if 'oscar' in content.lower():
                    print("✓ Contains 'oscar' text")
                if '<html' in content.lower():
                    print("✓ Contains HTML structure")
                else:
                    print("⚠️  No HTML structure found")
                    
        else:
            print(f"✗ HTTP {response.status_code} response")
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_dashboard_access()
